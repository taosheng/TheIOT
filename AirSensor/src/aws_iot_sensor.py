
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from general_air_quality import get_general_air_quality
import sys
import logging
import time
import json
import argparse

class shadowCallbackContainer:
	def __init__(self, deviceShadowInstance):
		self.deviceShadowInstance = deviceShadowInstance

	# Custom Shadow callback
	def customShadowCallback_Delta(self, payload, responseStatus, token):
		# payload is a JSON string ready to be parsed using json.loads(...)
		# in both Py2.x and Py3.x
		print("Received a delta message:"+payload)
		payloadDict = json.loads(payload)
		deltaMessage = payloadDict["state"]
                print(str(deltaMessage))
	        if u'action' in payloadDict["state"] and payloadDict["state"][u'action'] == 'do':
                        print("do check air again")
                        qname, ts, val = get_general_air_quality()
		        print("Request to update the reported air quality...")
                        deltaMessage['air quality'] = val
                        deltaMessage['action'] = 'wait'
		        newPayload = '{"state":{"reported":' + json.dumps(deltaMessage) + ', "desired":'+json.dumps(deltaMessage)+'}}'
                        print(newPayload)
		        self.deviceShadowInstance.shadowUpdate(newPayload, None, 5)
		        print("Sent.")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="ThingShadowEcho", help="Targeted client id")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
useWebsocket = args.useWebsocket
thingName = args.thingName
clientId = args.clientId

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
	parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
	exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
	parser.error("Missing credentials for authentication.")
	exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTShadowClient
myAWSIoTMQTTShadowClient = None
if useWebsocket:
	myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId, useWebsocket=True)
	myAWSIoTMQTTShadowClient.configureEndpoint(host, 443)
	myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(clientId)
	myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTShadowClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTShadowClient configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(thingName, True)
shadowCallbackContainer_Bot = shadowCallbackContainer(deviceShadowHandler)

# Listen on deltas
deviceShadowHandler.shadowRegisterDeltaCallback(shadowCallbackContainer_Bot.customShadowCallback_Delta)

# Loop forever
while True:
	time.sleep(5)
