# Elecrow CrowPanel Advance 7.0-HMI ESP32 AI Display

This is a custom ESPHome configuration for the Elecrow CrowPanel Advance 7.0-HMI ESP32 AI Display, powered by the ESP32 S3 N16R8. It uses the ESPHome ready-made project for the ESP32-S3-BOX-3 as a base, porting all of its primary features to the CrowPanel. 

This was written for a forthcoming XDA article. It will be updated over time. When using this, ensure that the S1 and S0 switches are both set to 0, so that both MIC and SPK are enabled. I updated the display logic to use LVGL and swapped the logic for changing the image displayed at any given time to show LVGL pages instaed. This has massively improved the performance of the display.

General design needs to be improved, but it is functional and significantly faster thanks to LVGL.

What works:

* Display
* Touchscreen (though no features currently require it)
* Microphone
* Showing response on screen
* Wake word detection
* Timers

What doesn't work:

* Display brightness control (not implemented yet)
* Timer ringers can only be turned off from the Home Assistant UI

Not tested:

* Audio output (theoretically should work, but I do not have a speaker to test it with)