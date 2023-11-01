import sys
import os

import serial
import argparse
import logging


__version__ = "0.01"

class Chain(serial.Serial):
    """Create Chain object.

    Harvard syringe pumps are daisy chained together in a 'pump chain'
    off a single serial port. A pump address is set on each pump. You
    must first create a chain to which you then add Pump objects.

    Chain is a subclass of serial.Serial. Chain creates a serial.Serial
    instance with the required parameters, flushes input and output
    buffers (found during testing that this fixes a lot of problems) and
    logs creation of the Chain.
    """
    def __init__(self, port):
        serial.Serial.__init__(self,port=port, stopbits=serial.STOPBITS_TWO, parity=serial.PARITY_NONE, timeout=2)
        self.flushOutput()
        self.flushInput()
        logging.info('Chain created on %s',port)

class Pump:
    """Create Pump object for Harvard Pump 11.

    Argument:
        Chain: pump chain

    Optional arguments:
        address: pump address. Default is 0.
        name: used in logging. Default is Pump 11.
    """
    def __init__(self, chain, address=0, name='Pump 11'):
        self.name = name
        self.serialcon = chain
        self.address = '{0:02.0f}'.format(address)
        self.diameter = None
        self.flowrate = None
        self.targetvolume = None

        """Query model and version number of firmware to check pump is
        OK. Responds with a load of stuff, but the last three characters
        are XXY, where XX is the address and Y is pump status. :, > or <
        when stopped, running forwards, or running backwards. Confirm
        that the address is correct. This acts as a check to see that
        the pump is connected and working."""
        try:
            self.write('VER')
            resp = self.read(17)
            if int(resp[1:3]) != int(self.address):
                raise PumpError('No response from pump at address %s' %
                                self.address)
        except PumpError:
            self.serialcon.close()
            raise

        logging.info('%s: created at address %s on %s', self.name,
                      self.address, self.serialcon.port)

    def write(self,command):
        msg = "{}{}\r".format(self.address, command)
        self.serialcon.write(msg.encode('utf-8'))

    def read(self,bytes=5):
        response = self.serialcon.read(bytes).decode()

        if len(response) == 0:
            raise PumpError('%s: no response to command' % self.name)
        else:
            return response

    def setdiameter(self, diameter):
        """Set syringe diameter (millimetres).

        Pump 11 syringe diameter range is 0.1-35 mm. Note that the pump
        ignores precision greater than 2 decimal places. If more d.p.
        are specificed the diameter will be truncated.
        """
        diameter = float(diameter) 
        if diameter > 35 or diameter < 0.1:
            raise PumpError('%s: diameter %s mm is out of range' % 
                            (self.name, diameter))

        # TODO: Got to be a better way of doing this with string formatting
        diameter = str(diameter)

        # Pump only considers 2 d.p. - anymore are ignored
        if len(diameter) > 5:
            if diameter[2] == '.': # e.g. 30.2222222
                diameter = diameter[0:5]
            elif diameter[1] == '.': # e.g. 3.222222
                diameter = diameter[0:4]

            print("back into the thick of it")
        
        msg ="diameter {}".format(diameter)     
        self.write(msg)    
        resp = self.read(50)
        if "error:" in resp: 
            print("Check your units or volume")
            print(resp)

    def setflowrate(self, flowrate, units):
        """Set flow rate (microlitres per minute).

        Flow rate is converted to a string. Pump 11 requires it to have
        a maximum field width of 5, e.g. "XXXX." or "X.XXX". Greater
        precision will be truncated.

        The pump will tell you if the specified flow rate is out of
        range. This depends on the syringe diameter. See Pump 11 manual.
        """
        flowrate = str(flowrate)
        units = str(units)

        if len(flowrate) > 5:
            flowrate = flowrate[0:5]
            logging.warning('%s: flow rate truncated to %s uL/min', self.name, 
                             flowrate)

        msg = "irate {} {}".format(flowrate, units)
        self.write(msg)
        resp = self.read(50)
        if "error:" in resp: 
            print("Check your units or flow rate")
            print(resp)
        
            
    def infuse(self):
        """Start infusing pump."""
        self.write('run')
        #resp = self.read(5)
        #while resp[-1] != '>':
        #    if resp[-1] == '<': # wrong direction
        #        self.write('wrun')
        #    else:
        #        raise PumpError('%s: unknown response to to infuse' % self.name)
        #    resp = self.serialcon.read(5)
        
        #logging.info('%s: infusing',self.name)
	

    def withdraw(self):
        """Start withdrawing pump."""
        self.write('REV')
        resp = self.read(5)
        
        while resp[-1] != '<':
            if resp[-1] == ':': # pump not running
                self.write('RUN')
            elif resp[-1] == '>': # wrong direction
                self.write('REV')
            else:
                raise PumpError('%s: unknown response to withdraw' % self.name)
                break
            resp = self.read(5)

        logging.info('%s: withdrawing',self.name)

    def stop(self):
        """Stop pump."""
        self.write('STP')
        #resp = self.read(5)
        #
        #if resp[-1] != ':':
        #    raise PumpError('%s: unexpected response to stop' % self.name)
        #else:
        #    logging.info('%s: stopped',self.name)

    def settargetvolume(self, targetvolume, units):
        """Set the target volume to infuse or withdraw (microlitres)."""

        msg = "tvolume {} {}".format(targetvolume, units)
        self.write(msg)
        resp = self.read(50)
        if "error:" in resp: 
            print("Check your units or volume")
            print(resp)

    def settargettime(self, targettime):
        """Set the target time to infuse or withdraw (sec)."""
        msg = "ttime {}".format(targettime) 

        self.write(msg)
        resp = self.read(50)
        if "error:" in resp: 
            print("Check your time")
            print(resp)

class PumpError(Exception):
    pass

# Command line options
# Run with -h flag to see help

def setup_logging(verbosity):
    log_fmt = ("%(levelname)s - %(module)s - "
               "%(funcName)s @%(lineno)d: %(message)s")
    # addl keys: asctime, module, name
    logging.basicConfig(filename=None,
                        format=log_fmt,
                        level=logging.getLevelName(verbosity))

def parse_command_line():
    parser = argparse.ArgumentParser(description="Analyse sensor data")
    parser.add_argument("-V", "--version", "--VERSION", action="version",
                        version="%(prog)s {}".format(__version__))
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        dest="verbosity", help="verbose output")
    # -h/--help is auto-added
    parser.add_argument("-add", "--address", dest="address",
                        # action="store",
                        nargs='+',
                        default=None, required=False, help="directories with data files")
    parser.add_argument("-d", "--dia", dest="diameter",
                        # action="store",
                        nargs='+',
                        default=None, required=False, help="directories with data files")
    parser.add_argument("-ir", "--infusion", dest="infusion",
                        # action="store",
                        nargs='+',
                        default=None, required=False, help="path to input")
    parser.add_argument("-iru", "--infusionunits", dest="infusionunits",
                        # action="store",
                        nargs='+',
                        default=None, required=False, help="path to input")
    parser.add_argument("-sf", "--setflow", dest="setflowrate",
                        # action="store",
                        nargs='+',
                        default=None, required=False, help="path to input")
    parser.add_argument("-st", "--settime", dest="settime",
                        # action="store",
                        nargs='+',
                        default=None, required=False, help="path to input")
    ret = vars(parser.parse_args())
    ret["verbosity"] = max(0, 30 - 10 * ret["verbosity"])

    return ret

def main():
    cmd_args = parse_command_line()
    setup_logging(cmd_args['verbosity'])
    chain = Chain(cmd_args['address'][0])
    chain = Chain(cmd_args['address'][0])
    p11 = Pump(chain,address=1) 
    p11.setdiameter(cmd_args['diameter'][0])  # mm
    p11.setflowrate(cmd_args['infusion'][0],cmd_args['infusionunits'][0])
    p11.settargettime(2)
    #p11.settargetvolume(1, "ml")
    p11.infuse()
    
    #p11.set_syringe_man("hm1")

    chain.close()


if "__main__" == __name__:
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("exited")

