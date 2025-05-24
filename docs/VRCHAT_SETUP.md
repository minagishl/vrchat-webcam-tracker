# VRChat Avatar Expression Setup Guide

To use facial expression tracking with VRChat avatars, you need to configure the following parameters in the animator controller.

## Required Parameters (Float type)

### Facial Expression Parameters

- MouthOpen (0.0-1.0): Mouth opening/closing
- LeftEyeBlink (0.0-1.0): Left eye blinking
- RightEyeBlink (0.0-1.0): Right eye blinking
- LeftEyebrowRaise (0.0-1.0): Left eyebrow raising
- RightEyebrowRaise (0.0-1.0): Right eyebrow raising
- MouthSmile (0.0-1.0): Smile

### Hand & Arm Parameters

- LeftArmRaise (0.0-1.0): Left arm raising
- RightArmRaise (0.0-1.0): Right arm raising
- LeftHandOpen (0.0-1.0): Left hand opening/closing
- RightHandOpen (0.0-1.0): Right hand opening/closing
- LeftHandFist (0.0-1.0): Left hand fist
- RightHandFist (0.0-1.0): Right hand fist
- LeftHandPoint (0.0-1.0): Left hand pointing
- RightHandPoint (0.0-1.0): Right hand pointing

## Unity Setup Steps

1. Open the avatar's AnimatorController
2. Add the above Float type parameters in the Parameters tab
3. Create animations corresponding to each parameter
4. Use Blend Trees to set up animations according to values

## VRChat OSC Configuration

1. Launch VRChat
2. Menu → Settings → OSC → Check Enable OSC
3. The application will automatically link when started

## Troubleshooting

### If OSC Connection Fails

- Check if OSC is enabled in VRChat
- Check firewall settings
- Verify IP address and port number are correct (default: 127.0.0.1:9000)

### If Tracking is Unstable

- Improve lighting (bright, uniform lighting)
- Adjust camera position (so face and hands fit in the screen)
- Adjust sensitivity in config.py

### If Frame Rate is Low

- Lower camera resolution (config.py)
- Close other applications
- Check CPU load
