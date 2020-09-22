import wshom
import logging

logging.basicConfig(level=logging.DEBUG)

a = wshom.create_app()
wshom.arrange_hangouts(a)
