import logging
import aiomysql
import asyncio

logger = logging.getLogger("pdnsbackup")
loop = asyncio.get_event_loop()

async def fetch(cfg: dict):
    records = []

    if cfg["gmysql_enable"]:
        logger.info("gmysql - backend enabled...")
        conn = None
        try:
            logger.debug("gmysql - connect to database...")
            conn = await aiomysql.connect( 
                        host=cfg['gmysql_host'], port=int(cfg['gmysql_port']),
                        user=cfg['gmysql_user'], password=cfg['gmysql_password'],
                        db=cfg['gmysql_dbname'], loop=loop
                    )
            logger.debug("gmysql - succesfully connected")

            logger.debug("gmysql - fetching records...")
            async with conn.cursor() as cur:
                await cur.execute("""
                            SELECT domains.name, records.name, records.type, ttl, content, prio 
                            FROM records INNER JOIN domains 
                            WHERE records.domain_id=domains.id
                        """)
                r = await cur.fetchall()
                records = list(r)
                logger.info("gmysql - %s records fetched..." % (len(records)))
        except Exception as e:
            logger.error("fetch - %s" % e)
        finally:
            if conn is not None:
                conn.close()
            logger.debug("gmysql - connection closed")
    return records