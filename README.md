# Adam Conway's Home Assistant Repository

This is Adam Conway's Home Assistant repository, which contains my more advanced configuration files, scripts, and ESPHome files for my home automation setup. Many of these have been included in XDA articles.

- [Automations](Automations)
- [ESPHome](ESPHome)

All of the projects in this repository are designed to be easily modified and adapted to your own home automation setup. They are intended to be used as a starting point for your own projects, and you can modify them to suit your needs. They are described below.


## Automations

### GoXLR fader light brightness

This automation adjusts the brightness of a specified light by adjusting the fader on a GoXLR Mini. This requires the GoXLR Utility integration, which can be found on HACS.

[XDA article](https://www.xda-developers.com/turned-goxlr-audio-interface-brightness-slider/)

### Light forecast colour

This automation changes the colour of a light based on the weather forecast and switches it on with that colour when the user's phone alarm goes off. It uses the Pirate Weather integration, which can be found on HACS. It can be modified to work with other weather integrations.

[XDA article](https://www.xda-developers.com/smart-light-weather-home-assistant/)

### LLM weather forecast notification

This automation sends a notification with the weather forecast for the day using a large language model (LLM) to dynamically generate the text. It uses the Pirate Weather integration, which can be found on HACS. It can be modified to work with other weather integrations. 

[XDA article](https://www.xda-developers.com/use-llm-dynamic-notifications-home-assistant/)

## ESPHome

### E-Ink Dashboard

![Image of the Seeed Studio XIAO 7.5-inch E-Ink display on a black chair, displaying the weather, a list of tasks, and a call scheduled for 14:15](Images/Seeed-Studios-XIAO-7.5-Inch-E-Ink-Display-Home-Assistant-1.jpg)

This is a dashboard for displaying weather information and more on an E-Ink display. It uses ESPHome and can be modified to display different pieces of information. It uses a template sensor defined in Home Assistant that will create a custom sensor and add attributes to it, which can be pulled to the dashboard. This dashboard uses the same concepts as, and directly lifts code in some parts from, the ESPHome Weatherman Dashboard by Madelena, found [here](https://github.com/Madelena/esphome-weatherman-dashboard/tree/main).  Currently, the weather is displayed on the left-hand side, and the right-hand side displays a list of Asana tasks and my next call, pulled from Google Calendar. I use the [Asana custom component](https://github.com/nitobuendia/asana-custom-component) for this. 

The dashboard is designed to be used with the [XIAO 7.5-inch ePaper Panel](https://www.seeedstudio.com/XIAO-7-5-ePaper-Panel-p-6416.html) in landscape, though should work with any project using the Waveshare 7.5-inch E-Ink display. This is currently a work in progress, and the project will be detailed on XDA in the coming days. 

### Elecrow CrowPanel Advance 7.0-HMI ESP32 AI Display

This is a voice assistant project that ports the ESP32-S3-BOX-3 ready-made project to the Elecrow CrowPaneL Advance 7.0-HMI ESP32 AI Display. It has full wake word and voice functionality. The long-term goal is complete feature parity with the ESP32-S3-BOX-3 project. It also sends a esphome.tts_uri event to Home Assistant with the URL for the audio response, thanks to the work done by [@formatBCE](https://github.com/formatBCE). This assistant is currently a work in progress, and has been [documented on XDA](https://www.xda-developers.com/built-google-home-hub-replacement-esp32-display/). It requires the S1 and S0 switches to be set to 0, so that both MIC and SPK are enabled. 

There are a number of improvements necessary to make this particular project more user-friendly, such as adding display brightness control.

### reTerminal E1001 E-Reader Project

This is an eReader project built using the reTerminal E1001, designed to demonstrate how an ESP32-S3 can be the backbone of a Kindle-esque device. It uses the green button to switch between reading mode and regular mode, and the two white buttons move forward and back.

It's a relatively janky setup that serves to demonstrate how, with a bit more polish, one could build a device like this using ESPHome. It pulls from a designated RSS feed and requires the Feedparser integration in Home Assistant.