#**********************************************************************************************
#
#  DSP Solutions
#  Ingenieure Kellermann, Voigt, Hoepfl, Eichler und Weidner, Partnerschaft
#  http://www.dspsolutions.de/
#
#  Author:      Oliver Eichler / Andreas Hegenauer
#  Email:       oliver.eichler@dspsolutions.de / andreas.hegenauer@lantiq.com
#  Phone:       +49-941-83055-1
#  FAX:         +49-941-83055-79
#
#  File:        Vr9MsgHandler.py
#
#  Module:
#
#  Description:
#
#  Created:     Aug. 27 2014
#
#  (C) 2014
#
#
#**********************************************************************************************
import vinax
import sys
from time import *

#import message filters (add the required path temporarily)
sys.path.append(sys.rootpath + "./scripts/Vinax_Common/Vr9MsgFilter")

# HERE YOU NEED TO ADD THE IMPORT OF YOUR MESSAGE FILTER MODULE
import ACK_ModemFSM_StateGet
import ACK_LineFailureNE_Get
import ACK_LineFailureFE_Get
import ACK_ModemFSM_FailReasonGet
import ACK_LineStatusUS_Get
import ACK_LineStatusDS_Get
import ACK_BearerChsUS_Get
import ACK_BearerChsDS_Get
import ACK_VersionInfoGet
import ACK_ADSL_FrameData_Get
import ACK_LinePerfCount_Get
import ACK_XTSE_StatusGet
import ACK_HS_StandardInfoFE_SPAR1Get
import ACK_ADSL_FrameDataDS_RTX_Get
import ACK_BearerChsDS_RTX_Get
import ACK_RTX_DS_MSG1InfoGet
import EVT_TR1Expiry
import EVT_OLR_EventGet
import ACK_DataPathFailuresGet
import ACK_LineStatusPerBandDS_Get
import ACK_ADSL_L2_ReqFailReasonGet
import ACK_ADSL_L2_StatsGet

sys.path = sys.path[:-1]

## handle incoming/outgoing CMV messages
#
# The object txmsg,rxmsg must be of type 'vinax.CMsg'.
# The attributes of CMsg are:
#   CMsg.ch       the channel number
#   CMsg.group    the group id
#   CMsg.address  the groups address
#   CMsg.index    the index for the data
#   CMsg.data     the payload data
#   CMsg.show     the flag which indicates whether the message is printed in the command window
#
#   mode: 
#    0 request CR
#    1 request CW
#    2 info CR
# You can add actions to take place on a specific message. However
# try to keep this file clean by using modules for the real work.
#


def cmv_messages(mode,txmsg,rxmsg):
    
    # Some helper variables to improve reading
    ModeCr   = 0
    ModeCw   = 1
    ModeInfo = 2

    # ----------------------------------------------------------------------------
    # ### Handle messages from Target to the DspSpy
    # ----------------------------------------------------------------------------
    # test for RX message and the right data type
    if rxmsg and isinstance(rxmsg,vinax.CMsg): 

        # Display all messages by default
        rxmsg.show = True

        # Check for error indication of VR9 message format
        if rxmsg.index & 0x8000:
            rxmsg.index = rxmsg.index & 0x7fff
            rxmsg.show = False
            print("> ch: %d group: %04X addr: %04X index: %04X error:" % (rxmsg.ch,rxmsg.group,rxmsg.address,rxmsg.index), end=' ', file=sys.stderr)
            for i in rxmsg.data:
                print("%04X" % i, end=' ', file=sys.stderr)
            if len(rxmsg.data):
                rxErr = rxmsg.data[0]
                if rxErr==0xffff:
                    print("-> Bad Message ID", end=' ', file=sys.stderr)
                elif rxErr==0xfffe: 
                    print("-> Write not allowed", end=' ', file=sys.stderr)
                elif rxErr==0xfffd: 
                    print("-> Read not allowed", end=' ', file=sys.stderr)
                elif rxErr==0xfffc: 
                    print("-> Bad offset", end=' ', file=sys.stderr)
                elif rxErr==0xfffb: 
                    print("-> FW Internal", end=' ', file=sys.stderr)
            print("", file=sys.stderr)
            return

        # Do not display acknowledges for write commands
        if mode == ModeCw: 
            rxmsg.show = False
        else:
            # ---- Provide time stamp ----
            timestamp = localtime()

            # ---- Message Filter start ----

            ## ---- Stat - Messages ----
            if rxmsg.group == vinax.stat and rxmsg.address == 0x00:       # Link Status
              ACK_ModemFSM_StateGet.evaluate(rxmsg, timestamp)
              rxmsg.show = False
              #if mode == ModeInfo:
              #    rxmsg.show = False


            elif rxmsg.group == vinax.stat and rxmsg.address == 0x01:     # ACK_XTSE_StatusGet
              ACK_XTSE_StatusGet.evaluate(rxmsg)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.stat and rxmsg.address == 0xff:     # Modem Ready
              ACK_ModemFSM_StateGet.evaluate(rxmsg, timestamp)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.stat and rxmsg.address == 0x05:     # Fail Reason
              ACK_ModemFSM_FailReasonGet.evaluate(rxmsg)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.stat and rxmsg.address == 0x80:     # EVT_TR1Expiry
              EVT_TR1Expiry.evaluate(rxmsg, timestamp)
              if mode == ModeInfo:
                  rxmsg.show = False

            ## ---- Rate - Messages ----
            elif rxmsg.group == vinax.rate and rxmsg.address == 0x00 and len(rxmsg.data) >= 16:     # Upstream Rate
              ACK_BearerChsUS_Get.evaluate(rxmsg)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.rate and rxmsg.address == 0x01 and len(rxmsg.data) >= 16:     # Downstream Rate
              ACK_BearerChsDS_Get.evaluate(rxmsg)
              if mode == ModeInfo:
                  rxmsg.show = True
            
            elif rxmsg.group == vinax.rate and rxmsg.address == 0x02:     # ACK_BearerChsDS_RTX_Get
              ACK_BearerChsDS_RTX_Get.evaluate(rxmsg)
              rxmsg.show = True

            ## ---- Plam - Messages ----
            elif rxmsg.group == vinax.plam and rxmsg.address == 0x00:     # Line Failure NE
              ACK_LineFailureNE_Get.evaluate(rxmsg, timestamp)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.plam and rxmsg.address == 0x01:     # Line Failure FE
              ACK_LineFailureFE_Get.evaluate(rxmsg, timestamp)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.plam and rxmsg.address == 0x03:     # EVT_OLR_US_EventGet
              dir=0  # US direction
              EVT_OLR_EventGet.evaluate(rxmsg,dir,timestamp)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.plam and rxmsg.address == 0x04:     # EVT_OLR_DS_EventGet
              dir=1  # DS direction
              EVT_OLR_EventGet.evaluate(rxmsg,dir,timestamp)
              if mode == ModeInfo:
                  rxmsg.show = True

            ## ---- Info - Messages ----
            elif rxmsg.group == vinax.info and rxmsg.address == 0x45:     # Line Status US Get
              ACK_LineStatusUS_Get.evaluate(rxmsg)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0x44:     # Line Status DS Get
              ACK_LineStatusDS_Get.evaluate(rxmsg)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0x17:     # SNR,BAT FGain
              rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0x0B:     # SNR,BAT FGain
              rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0x19:     # SNR,BAT FGain
              rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0xCB:     # ACK_HS_StandardInfoFE_SPAR1Get (CB03)
              ACK_HS_StandardInfoFE_SPAR1Get.evaluate(rxmsg)
              rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0xD2:     #  ACK_LineStatusPerBandDS_Get (D203)
              ACK_LineStatusPerBandDS_Get.evaluate(rxmsg,0)
              rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0xD3:     #  ACK_LineStatusPerBandUS_Get (D303)
              ACK_LineStatusPerBandDS_Get.evaluate(rxmsg,1)
              rxmsg.show = True

            elif rxmsg.group == vinax.info and rxmsg.address == 0xE5:     # reuse ACK_ADSL_FrameDataDS_RTX_Get (E503)
              ACK_ADSL_FrameDataDS_RTX_Get.evaluate(rxmsg)
              rxmsg.show = True

            ## ---- IFX - Messages ----
            elif rxmsg.group == 0x10 and rxmsg.address == 0x00:           # Firmware Version (0010)
              ACK_VersionInfoGet.evaluate(rxmsg)
              if mode == ModeInfo:
                  rxmsg.show = True

            elif rxmsg.group == 0x13 and rxmsg.address == 0x20:           # ACK_DataPathFailuresGet (2013)
              ACK_DataPathFailuresGet.evaluate(rxmsg,timestamp)
              rxmsg.show = True

            ## ---- Ainf - Messages ----
            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x01:     # ADSL FrameData DS Lp0/Interleaved
              dir=1  # DS direction
              path=0  # latency path 0 (interleaved path in G.DMT)
              ACK_ADSL_FrameData_Get.evaluate(rxmsg,dir,path)
              rxmsg.show = True

            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x02:     # ADSL FrameData US Lp0/Interleaved
              dir=0  # US direction
              path=0  # latency path 0 (interleaved path in G.DMT)
              ACK_ADSL_FrameData_Get.evaluate(rxmsg,dir,path)
              rxmsg.show = True

            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x03:     # ADSL FrameData DS Lp1/Fast (030E)
              dir=1  # DS direction
              path=1  # latency path 1 (fast path in G.DMT)
              ACK_ADSL_FrameData_Get.evaluate(rxmsg,dir,path)
              rxmsg.show = True

            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x04:     # ADSL FrameData US Lp1/Fast (040E)
              dir=0  # US direction
              path=1  # latency path 1 (fast path in G.DMT)
              ACK_ADSL_FrameData_Get.evaluate(rxmsg,dir,path)
              rxmsg.show = True

            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x0B:     # ACK_ADSL_L2_StatsGet (0B0E)
              ACK_ADSL_L2_StatsGet.evaluate(rxmsg)
              rxmsg.show = False

            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x0C:     # ACK_ADSL_L2_ReqFailReasonGet (0C0E)
              ACK_ADSL_L2_ReqFailReasonGet.evaluate(rxmsg, timestamp)
              rxmsg.show = False

            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x0D:     # ACK_ADSL_FrameDataDS_RTX_Get (0D0E)
              ACK_ADSL_FrameDataDS_RTX_Get.evaluate(rxmsg)
              rxmsg.show = True

            elif rxmsg.group == vinax.ainf and rxmsg.address == 0x0E:     # ACK_RTX_DS_MSG1InfoGet (0E0E)
              ACK_RTX_DS_MSG1InfoGet.evaluate(rxmsg)
              rxmsg.show = True

            ## ---- Cntr - Messages ----
            elif rxmsg.group == vinax.cntr and rxmsg.address == 0x02:     # ACK_LinePerfCountNE_Get (Running)
              dir=0  # NE direction (0), FE direction (1)
              run=1  # running counter (1), or TR1 counter (0)
              ACK_LinePerfCount_Get.evaluate(rxmsg,dir,run,timestamp)
              rxmsg.show = True

            elif rxmsg.group == vinax.cntr and rxmsg.address == 0x03:     # ACK_LinePerfCountNE_Get (TR1)
              dir=0  # NE direction (0), FE direction (1)
              run=0  # running counter (1), or TR1 counter (0)
              ACK_LinePerfCount_Get.evaluate(rxmsg,dir,run,timestamp)
              rxmsg.show = True

            elif rxmsg.group == vinax.cntr and rxmsg.address == 0x04:     # ACK_LinePerfCountFE_Get (Running)
              dir=1  # NE direction (0), FE direction (1)
              run=1  # running counter (1), or TR1 counter (0)
              ACK_LinePerfCount_Get.evaluate(rxmsg,dir,run,timestamp)
              rxmsg.show = True

            elif rxmsg.group == vinax.cntr and rxmsg.address == 0x05:     # ACK_LinePerfCountFE_Get (TR1)
              dir=1  # NE direction (0), FE direction (1)
              run=0  # running counter (1), or TR1 counter (0)
              ACK_LinePerfCount_Get.evaluate(rxmsg,dir,run,timestamp)
              rxmsg.show = True

            # ---- Message Filter end ----

        # Disable message printing in the command window on request
        if vinax.ShowMsg==False:
            rxmsg.show = False

    # ----------------------------------------------------------------------------
    # ### Handle messages from DspSpy to Target
    # ----------------------------------------------------------------------------
    # test for TX message and the right data type
    if txmsg and isinstance(txmsg,vinax.CMsg): 

        # Display all messages by default
        txmsg.show = True

        # Do not display write commands
#        if mode == ModeCw: 
#          txmsg.show = False

        # Do not display read commands
        if mode == ModeCr: 
          txmsg.show = False

        # Disable message printing in the command window on request
        if vinax.ShowMsg==False:
            txmsg.show = False

# end of cmv_messages(msg)

############################################################
# this will be called during import to set
# the CMV message handler and enable the messages for the
# command window

# Install message function
vinax.procCMV = cmv_messages

# Enable message display
vinax.ShowMsg = True

# Check for DTI interface and install wrapper
if "DTI" in vinax.name:
    import Vr9MsgHandler_Dti
