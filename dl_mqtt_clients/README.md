This module provides necessary tools to implement and extend serving a deep learning model with data streaming in and result stream out using the MQTT protocol.

For example, the mosqeras class abstracts the combination of keras and mqtt and includes a data mqtt client, config mqtt client and a kerasnn class. Typically, different pre/postprocessing steps will necesittate 
a new class that extends the original mosqeras abstract class. 
