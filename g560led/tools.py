def set_loger_config(log_location:str=None, **kwargs):
	import logging
	from os.path import expanduser, join

	handlers = (
		logging.FileHandler(
			log_location if log_location is not None else join(expanduser('~'), f"g560/logs/{dt.now():%Y-%m-%dT%H:%M:%S}.log"),
			mode='w'),
		logging.StreamHandler()
	)

	logging_format = logging.Formatter(
		"%(levelname)5s %(asctime)s.%(msecs)03d - PID: %(process)s - Thread: %(thread)d - %(name)s - Function: %(funcName)s() in %(filename)s on line %(lineno)3d - %(message)s",
		"%m/%d/%Y %H:%M:%S")
	for handler in handlers:
		handler.setFormatter(logging_format)

	logging.basicConfig(level=logging.DEBUG,
						handlers=handlers,
						force=kwargs.get("force", True))
