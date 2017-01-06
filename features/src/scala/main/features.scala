package main.scala

import _root_.org.apache.spark.rdd.RDD
import _root_.org.apache.spark.SparkContext
import _root_.org.apache.spark.SparkContext._
import _root_.org.apache.spark.SparkConf
import _root_.org.apache.spark.sql.SaveMode


import _root_.scala.collection.mutable.WrappedArray
import _root_.org.apache.spark.sql.Row
import _root_.org.apache.spark.sql.functions.{col, first}
import _root_.org.apache.spark.sql.Column


case class ParticipantInfo(
    assists: Long,
    cs10: Double,
    cs20: Double,
    csDiff10: Double,
    csDiff20: Double,
    deaths: Long,
    goldEarned: Long,
    gpm10: Double,
    gpm20: Double,
    kills: Long,
    lane: String,
    largestKillingSpree: Long,
    role: String,
    summonerId: String,
    team: String,
    totalDamageDealt: Long,
    totalDamageDealtToChampions: Long,
    totalDamageTaken: Long,
    totalTimeCrowdControlDealt: Long,
    winner: Boolean,
    xpDiff10: Double,
    xpDiff20:Double
)

case class ParticipantMatch(matchId: String, summ_id: String, p_match_id: String, summ_pos: Int, team: String, winner: Boolean,  matchDuration: Long, participants: Array[ParticipantInfo])

case class Ret(
    winningTeam: String,
    matchId: String,
    playerNum: Int,
    winrate: Float,
    GPM: Float,
    KDA: Float,
    KD: Float,
    largestKillingSpree: Float,
    totalDamageDealt: Float,
    totalDamageDealtToChampions: Float,
    totalDamageTaken: Float,
    totalTimeCrowdControlDealt: Float,
    cs10: Float,
    cs20: Float,
    csDiff10: Float,
    csDiff20: Float,
    gpm10: Float,
    gpm20: Float,
    xpDiff10: Float,
    xpDiff20: Float
)



object Features {
  def main(args: Array[String]) {

    val conf = new SparkConf().setAppName("Features gen")
//                 .setMaster("yarn-cluster")

    val sc = new SparkContext(conf)

    val sqlContext = new org.apache.spark.sql.SQLContext(sc)
    import sqlContext.implicits._
    implicit def bool2int(b:Boolean) = if (b) 1 else 0


    val inputPath = "hdfs:///user/ahaeflig/"
    val outputPath = "hdfs:///user/ahaeflig/out/"

    // val inputPath = "file:///Users/Marco/Google Drive/HEC/ada/proj/repo/ada-project/crawler_by_match/"
    // val outputPath = "file:///Users/Marco/Google Drive/HEC/ada/proj/repo/ada-project/out/"

    val processed_matches = sqlContext.read.json(inputPath + "processed_matches.json")

    val summs_matches = sqlContext.read.json(inputPath + "summ_matches.json")

    val matches = sqlContext.read.json(inputPath + "matches.json")

    // join processed_matches with the summoner_ids of that match (on match_id) and generate pos of the player
    val participants = processed_matches.join(matches, $"p_match_id" === $"matchId").drop("matchId").map(x => {
        def generate_pos (pos: Any, role: Any):Int = {
            (pos, role) match { // TODO generate position wrt the game + team (so we have 1 -> 5 consistent)
                case ("BOTTOM", "DUO_CARRY") => 1
                case ("MIDDLE", "SOLO") => 2
                case ("TOP", "SOLO") => 3
                case ("JUNGLE", _) => 0 // sometimes there are several junglers
                case ("BOTTOM", "DUO_SUPPORT") => 5
                // case ("BOTTOM", "DUO") => 0
                // case ("BOTTOM", "NONE") => 0
                case _ => 0
            }
        }

        def fill_pos(matchInfo: (Int, String, String, Boolean, Long), participant_info: WrappedArray[(Int, String, String, Boolean, Long)]) = {
            val summ_id = matchInfo._2
            val team = matchInfo._3
            val players_in_team = participant_info.filter(x => x._3 == team)

            val players_with_pos = players_in_team.filter(_._1 != 0)
            val found_pos = players_with_pos.map(_._1).toSet
            val missing_pos =  (1 to 5).toSet.diff(found_pos).toList.sorted

            val players_without_pos = players_in_team.filter(_._1 == 0).toList.sortWith(_._5 > _._5)

            val pos = players_without_pos.zip(missing_pos).filter(_._1._2 == summ_id).head._2

            pos
        }

        val participant_info = x(2) match {
                case matchInfo: WrappedArray[Row] => matchInfo.map(p => (
                    generate_pos(p(10), p(12)), // pos_num (lane, role)
                    p(13).asInstanceOf[String], // summoner_id
                    p(14).asInstanceOf[String], // team
                    p(19).asInstanceOf[Boolean], // winner
                    p(6).asInstanceOf[Long] // gold (tmp for the pos finding)
                ))
            }

        // sort the players that didn't get a pos by their gold to fill the gaps
        val final_participant_info = participant_info.map(matchInfo => (
            if (matchInfo._1 == 0) fill_pos(matchInfo, participant_info) else matchInfo._1,
            matchInfo._2,
            matchInfo._3,
            matchInfo._4
            )
        )

        (x(0).asInstanceOf[String], final_participant_info)
        }).toDF("p_match_id", "summs_infos")


    // flatten the participants
    val participants_flat = participants.explode("summs_infos", "summ_info"){x:WrappedArray[(Integer, String, String, Boolean)] => x}.
    drop("summs_infos").map(x => {
        val participant_info = x(1) match {
                case p: Row => (p(0).asInstanceOf[Integer], p(1).asInstanceOf[String], p(2).asInstanceOf[String], p(3).asInstanceOf[Boolean])
                // case _ => ("a", "a")
            }
        (x(0).asInstanceOf[String], participant_info._1, participant_info._2, participant_info._3, participant_info._4)
        }).toDF("p_match_id", "summ_pos", "summ_id", "team", "winner")


    // participants_flat.select("summ_pos").groupBy("summ_pos").count().show()
    // participants_flat.filter(participants_flat("summ_pos") === "0").show

    // join with the list of matches of the player (on summ_id)
    val participants_matches_ids = participants_flat.join(summs_matches, "summ_id")

    // flatten the list of matches
    val participants_matches_ids_flat = participants_matches_ids.explode("matches", "matchId"){x:WrappedArray[String] => x}.drop("matches")

    // join with the matches (on match_id)  and convert to dataset
    val participants_matches = participants_matches_ids_flat.join(matches.select($"matchId", $"matchDuration", $"participants"), "matchId").as[ParticipantMatch]


    participants_matches_ids_flat.join(matches.select($"matchId", $"matchDuration"), "matchId")
    // generate features
    val features = participants_matches.groupBy($"p_match_id", $"summ_id", $"summ_pos", $"team", $"winner").flatMapGroups((key, rows) => {
        val summId = key(1).asInstanceOf[String]

        def getInfos(participantMatch:ParticipantMatch):ParticipantInfo = {
            participantMatch.participants.filter(x => x.summonerId == summId)(0)
        }
        val matchId = key(0).asInstanceOf[String]

        // remove the tested match from the list of recent games
        val games = rows.toList.filter(x => x.matchId != matchId)

        val totalGames = games.length

        /* winrate */
        val wins = games.foldLeft(0)((acc, game) => getInfos(game).winner.toInt + acc)

        val winrate = wins.toFloat / totalGames

        /* GPM */
        val GPM = 60f * games.foldLeft(0.toLong)((acc, game) => getInfos(game).goldEarned + acc).toFloat / games.foldLeft(0.toLong)((acc, game)  => game.matchDuration + acc)

        /* KDA */
        val kills = games.foldLeft(0)((acc, game) => getInfos(game).kills.toInt + acc)
        val assists = games.foldLeft(0)((acc, game) => getInfos(game).assists.toInt + acc)
        val deaths = games.foldLeft(0)((acc, game) => getInfos(game).deaths.toInt + acc)

        val KDA = (kills+deaths).toFloat / math.max(deaths, 1)
        val KD = kills.toFloat / math.max(deaths, 1)

        def averageInt(getMember: ParticipantInfo => Int): Float = {
            def summed = games.foldLeft(0)((acc, game) => getMember(getInfos(game)) + acc)
            math.max(summed, 1).toFloat / totalGames
        }

        /* largestKillingSpree */
        val largestKillingSpree = averageInt(_.largestKillingSpree.toInt)

        /* totalDamageDealt */
        val totalDamageDealt = averageInt(_.totalDamageDealt.toInt)


        /* totalDamageDealtToChampions */
        val totalDamageDealtToChampions = averageInt(_.totalDamageDealtToChampions.toInt)

       /* totalDamageTaken */
        val totalDamageTaken = averageInt(_.totalDamageTaken.toInt)

       /* totalTimeCrowdControlDealt */
        val totalTimeCrowdControlDealt = averageInt(_.totalTimeCrowdControlDealt.toInt)


        /* timeline stuff */
        def averageDouble(getMember: ParticipantInfo => Double): Float = {
            def summed = games.foldLeft(0.0)((acc, game) => getMember(getInfos(game)) + acc)
            math.max(summed, 1).toFloat / totalGames
        }

        val cs10 = averageDouble(_.cs10)
        val cs20 = averageDouble(_.cs20)

        val csDiff10 = averageDouble(_.csDiff10)
        val csDiff20 = averageDouble(_.csDiff20)

        val gpm10 = averageDouble(_.gpm10)
        val gpm20 = averageDouble(_.gpm20)

        val xpDiff10 = averageDouble(_.xpDiff10)
        val xpDiff20 = averageDouble(_.xpDiff20)

        def computePlayerNum (pos: Int, team: String): Int = {
            if (team == "blue") pos
            else 5 + pos
        }

        def winningTeam(winner:Boolean, team:String): String = {
            if (winner) team
            else if (team == "blue") "purple"
            else "blue"
        }
        val ret = Ret(
            winningTeam(key(4).asInstanceOf[Boolean], key(3).asInstanceOf[String]), // winning team
            key(0).asInstanceOf[String], // match_id
            // key(1).asInstanceOf[String], // summ_id
            computePlayerNum(
                key(2).asInstanceOf[Int], // pos
                key(3).asInstanceOf[String] // team
            ),
            winrate, GPM, KDA, KD, largestKillingSpree, totalDamageDealt, totalDamageDealtToChampions, totalDamageTaken, totalTimeCrowdControlDealt,
            cs10, cs20, csDiff10, csDiff20, gpm10, gpm20, xpDiff10, xpDiff20
            )
        List(ret)
    }).toDF()

    // out of memory in spark-shell?
    // features_f.select($"c").groupBy($"c").count().show()

    // pivot (reshape long to wide)
    val mapping: Map[String, Column => Column] = Map("first" -> first)

    val groupBy = Seq("winningTeam", "matchId")
    val aggregate = Seq(
        "winrate", "GPM", "KDA", "KD", "largestKillingSpree", "totalDamageDealt",
        "totalDamageDealtToChampions", "totalDamageTaken","totalTimeCrowdControlDealt",
        "cs10", "cs20", "csDiff10", "csDiff20", "gpm10", "gpm20", "xpDiff10", "xpDiff20"
        )
    val operations = Seq("first")
    val exprs = aggregate.flatMap(c => operations .map(f => mapping(f)(col(c))))

    val out = features.groupBy(groupBy.map(col): _*).pivot("playerNum", (1 to 10).toList).agg(exprs.head, exprs.tail: _*)

    // out.show

    // // tmp
    // val tmp = participants_matches_ids.select($"summ_id", $"p_match_id", $"matches").map(x => (x(0).asInstanceOf[String], x(1).asInstanceOf[String], x(2).asInstanceOf[WrappedArray[String]].length)).toDF("a", "b", "c")
    // tmp.filter(tmp("c") !== 2).show

    // check
    // features.groupBy($"_3").count().show

    // participants_matches.select(col("participants").as[Array[ParticipantInfo]])

    // participants_matches.select(col("team").as[String])

    // participants_matches.select(($"team").as[String]).show



    out.coalesce(1).write.mode(SaveMode.Overwrite).format("com.databricks.spark.csv").save(outputPath + "out.csv")

    sc.stop()
  }
}
