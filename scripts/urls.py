#coding:utf-8
import app
from app.gm.auth import(
    Handler_Login,
    Handler_Logout,
    Handler_AccountManage,
    Handler_TestAccount,
    Handler_TestRecharge,
    )
from app.gm.main import(
    Handler_Index,
    )
from app.gm.serverlist import(
    Handler_ServerList,
    )

from app.private.server import(
    Handler_Game_Status,
    Handler_Battle_Status,
    Handler_Connector_Status,

    )
from app.private.ranks import(
    Handler_Update_Ranks,
    )
from app.private.auth import(
    Handler_PlayerCreate,
    Handler_PlayerOnLine,
    )
from app.private.pay import(
    Handler_Pay,
    )
from app.private.rankaward import(
    Handler_Ranks_Award,
    )

from app.client.client import(
    Handler_CL_CheckPermission,
    Handler_CL_Ranks,
    Handler_CL_ServerLists,
    Handler_CL_Login,
    Handler_CL_RegisterID
    )

from app.client.authorize import(
    Handler_Check_Authorize,
    )

from app.gm.servermanage import(
       handler_BoardOrBusy,
       Handler_GM_PlayerInfo,
       Handler_GM_GameMail,
       Handler_GM_MailManage,
       Handler_GM_SendCloudMsg
    )
from app.gm.serverdebug import(
        Handler_ServerDebug,
    )
from app.gm.playerlog import Handler_PlayerLog

from app.gm.paysystem import Handler_GM_OrderInfo
from app.gm.googlecloudmsg import Handler_GM_GCM
from app.gm.guildinfo import Handler_GM_GuildInfo
from app.gm.sms import Handler_GM_SMS
from app.analysis.loganalysis import(
    Handler_LA_Pay,
    Handler_LA_ConsumeGold,
    Handler_LA_DailyActive,
    Handler_LA_ConsumeGoldByAct,
    Handler_LA_DailyCreate,
    Handler_LA_VipLevel,
    Handler_LA_Subsistence,
    Handler_LA_ItemSoldInMall,
    Handler_LA_LevelDistribution,
    Handler_LA_GoldMoneySurplus,
    Handler_LA_TotalOnlineTime,
    Handler_LA_ConsumeGoldBySys,
    Handler_LA_DailyCreateCountByTime,
    Handler_LA_CurOnlineCountByTime
    )

from app.pay.PaySystem_HaiWan import HandlerPayHaiWan
from app.pay.PaySystem_SY185 import HandlerPaySY185
from app.pay.PaySystem_HuaWei import HandlerPayHuaWei
from app.pay.PaySystem_Oppo import HandlerPayOppo
from app.pay.PaySystem_Vivo import HandlerPayVivoTrade
from app.pay.PaySystem_7659 import HandlerPay7659
from app.pay.PaySystem_CoolPad import HandlerPayCoolPad
from app.pay.PaySystem_JinLi import HandlerPayJinLi
gmhandlers = [
            (r"/", Handler_Login),
            (r"/gm", Handler_Login),
            (r"/gm/login", Handler_Login),
            (r"/gm/logout", Handler_Logout),
            (r"/gm/accman", Handler_AccountManage),
            (r"/gm/main", Handler_Index),
            (r"/gm/serverlist", Handler_ServerList),
            (r"/gm/boardorbusy",handler_BoardOrBusy),
            (r"/gm/playerinfo", Handler_GM_PlayerInfo),
            (r"/gm/playerlog", Handler_PlayerLog),
            (r"/gm/gamemail", Handler_GM_GameMail),
            (r"/gm/mailmanage", Handler_GM_MailManage),
            (r"/gm/serverdebug", Handler_ServerDebug),
            (r"/gm/testaccount", Handler_TestAccount),
            (r"/gm/testrecharge", Handler_TestRecharge),
            (r"/gm/cloudmessage", Handler_GM_GCM),
            (r"/gm/guildinfo", Handler_GM_GuildInfo),
            (r"/gm/la_pay", Handler_LA_Pay),
            (r"/gm/la_consumegold", Handler_LA_ConsumeGold),
            (r"/gm/la_dailyactive", Handler_LA_DailyActive),
            (r"/gm/la_consumegoldbyact", Handler_LA_ConsumeGoldByAct),
            (r"/gm/la_dailycreate", Handler_LA_DailyCreate),
            (r"/gm/la_viplevel", Handler_LA_VipLevel),
            (r"/gm/la_subsistence", Handler_LA_Subsistence),
            (r"/gm/la_itemsoldinmall", Handler_LA_ItemSoldInMall),
            (r"/gm/la_leveldistribution", Handler_LA_LevelDistribution),
            (r"/gm/la_goldmoneysurplus", Handler_LA_GoldMoneySurplus),
            (r"/gm/la_totalonlinetime", Handler_LA_TotalOnlineTime),
            (r"/gm/la_consumegoldbysys", Handler_LA_ConsumeGoldBySys),
            (r"/gm/la_dccountbytime", Handler_LA_DailyCreateCountByTime),
            (r"/gm/la_cocountbytime", Handler_LA_CurOnlineCountByTime),
            (r"/gm/orderinfo", Handler_GM_OrderInfo),
            (r"/gm/sms", Handler_GM_SMS)
]
handlers = [
            #gameserver to webcenter
            (r"/private/game_status", Handler_Game_Status),
            (r"/private/battle_status", Handler_Battle_Status),
            (r"/private/connector_status", Handler_Connector_Status),
            (r"/private/update_ranks", Handler_Update_Ranks),
            (r"/private/player_create", Handler_PlayerCreate),
            (r"/private/player_online", Handler_PlayerOnLine),
            (r"/private/pay", Handler_Pay),
            (r"/private/ranks_award", Handler_Ranks_Award),
            #client from webcenter
            (r"/permission", Handler_CL_CheckPermission),
            (r"/loginex", Handler_CL_Login),
            (r"/svrlists", Handler_CL_ServerLists),
            (r"/ranks", Handler_CL_Ranks),
            (r"/registerid", Handler_CL_RegisterID),
            (r"/vertifyaccount", Handler_Check_Authorize),
            #pay for PayServer
            (r"/pay_haiwan", HandlerPayHaiWan),
            (r"/sy185", HandlerPaySY185),
            (r"/HuaWei", HandlerPayHuaWei),
            (r"/Oppo", HandlerPayOppo),
            (r"/vivotrade", HandlerPayVivoTrade),
            (r"/ky7659", HandlerPay7659),
            (r"/CoolPad", HandlerPayCoolPad),
            (r"/JinLi", HandlerPayJinLi),
        ]