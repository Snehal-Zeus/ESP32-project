# ESP32-project
## Iot based disaster management with AI

### Objective
The main goal of this project was to build a smart system that can detect disasters like earthquakes, fires, floods, and gas leaks using sensors and Artificial Intelligence (AI). The idea was to use IoT (Internet of Things) technology to collect data from the environment and then use an AI model to understand and identify if a disaster is happening. The system should give quick alerts so that people can take action on time. The project also aimed to create a system that is affordable, accurate, and can be used in both cities and villages to help improve safety.

### Work Done
To start the project, the right sensors were chosen for detecting each type of disaster. 
An accelerometer (ADXL345) was used for sensing earthquakes by measuring vibrations. 
An IR-flame sensor was used to detect fire, and a gas sensor (MQ2) was used to identify gas leaks. 
For flood detection, an ultrasonic sensor (HC-SR04) was placed above the ground to measure rising water levels, and a flow sensor (YF-S201) was used to check water flow rate.

On detection of the disasters from the variuos sensors and  according to their intensities(thresholds) various warnings and signals were produced as output. The warning lights were 
-- Blue Led & 1s of Buzzer sound-- for lower level warning.
-- Red Led & 3s of Buzzer sound-- for critical/higher level warning.
-- LCD display-- to show the disaster type and warnings, intensities.

The next step was to collect data from these sensors and use it to train an AI model. This model learned to identify which type of disaster is happening based on the sensor values. After the model was trained, it was used in the system to make real-time decisions. If the model detects a disaster, it triggers alerts using lights or a buzzer. The system was tested to make sure it works correctly and can give alerts quickly.

Different  ML models were used to classify the disasters as well as predict the water level based on the water height and water flow rate. And the following outputs were obtained.

