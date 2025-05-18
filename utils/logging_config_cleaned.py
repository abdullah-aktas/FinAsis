import logging
import configparser
import os

def fileConfig(fname, defaults=None, disable_existing_loggers=True, encoding=None):
    """Load logging configuration from .ini-style file."""
    if isinstance(fname, str):
        if not os.path.exists(fname):
            raise FileNotFoundError(f"{fname} doesn't exist")
        elif not os.path.getsize(fname):
            raise RuntimeError(f"{fname} is an empty file")

    cp = configparser.ConfigParser(defaults)
    cp.read_file(fname if hasattr(fname, 'readline') else open(fname, encoding=encoding or 'utf-8'))

    formatters = _create_formatters(cp)
    logging.shutdown()  # Tüm mevcut handler'ları kapatır

    # Kök logger'dan tüm handler'ları kaldır
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    handlers = _install_handlers(cp, formatters)
    _install_loggers(cp, handlers, disable_existing_loggers)

# Aşağıdaki yardımcı fonksiyonları da ekleyin:
def _create_formatters(cp):
    formatters = {}
    flist = map(str.strip, cp.get("formatters", "keys").split(","))
    for form in flist:
        sect = f"formatter_{form}"
        fmt = cp.get(sect, "format", fallback=None)
        dfmt = cp.get(sect, "datefmt", fallback=None)
        style = cp.get(sect, "style", fallback='%')
        formatter_class = cp.get(sect, "class", fallback="logging.Formatter")
        Formatter = _resolve(formatter_class)
        formatters[form] = Formatter(fmt, dfmt, style)
    return formatters

def _install_handlers(cp, formatters):
    handlers = {}
    hlist = map(str.strip, cp.get("handlers", "keys").split(","))
    for hname in hlist:
        sect = f"handler_{hname}"
        klass = _resolve(cp.get(sect, "class"))
        args = eval(cp.get(sect, "args", fallback='()'))
        handler = klass(*args)
        level = cp.get(sect, "level", fallback=None)
        if level:
            handler.setLevel(level)
        fmt = cp.get(sect, "formatter", fallback=None)
        if fmt:
            handler.setFormatter(formatters[fmt])
        handlers[hname] = handler
    return handlers

def _install_loggers(cp, handlers, disable_existing):
    loggers = map(str.strip, cp.get("loggers", "keys").split(","))
    for lname in loggers:
        sect = f"logger_{lname}" if lname != "root" else "logger_root"
        log = logging.getLogger(cp.get(sect, "qualname", fallback=""))
        log.handlers.clear()
        for h in map(str.strip, cp.get(sect, "handlers", fallback="").split(",")):
            if h:
                log.addHandler(handlers[h])
        level = cp.get(sect, "level", fallback=None)
        if level:
            log.setLevel(level)
        log.disabled = False
        log.propagate = cp.getboolean(sect, "propagate", fallback=True)

def _resolve(name):
    """Resolve a dotted object name to a Python object."""
    parts = name.split('.')
    mod = __import__(parts[0])
    for p in parts[1:]:
        mod = getattr(mod, p)
    return mod 