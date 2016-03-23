# -*- coding: utf-8 -*-
"""
This file provides very simple workflows for testing purposes.
Do not delete, otherwise 'verdi developertest' will stop to work.
"""

from aiida.orm import Calculation
import aiida.workflows2.util as util
from aiida.workflows2.process import FunctionProcess
import threading

__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.5.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi, Martin Uhrin"


def wf(func):
    import inspect
    import itertools

    def wrapped_function(*args, **kwargs):
        """
        This wrapper function is the actual function that is called.
        """
        # Build up the Process representing this function
        FuncProc = FunctionProcess.build(func, **kwargs)

        # Use thread-local storage for the stack
        try:
            stack = threading.local()._wf_stack
        except AttributeError:
            threading.local()._wf_stack = []
            stack = threading.local()._wf_stack

        if stack:
            # TODO: This is where a call link would go from prent to this fn
            pass

        stack.append(func)
        # Run the wrapped function
        proc = FuncProc.create()

        # Bind the input values to the input ports
        for k, v in dict(
                itertools.chain(
                    itertools.izip(inspect.getargspec(func)[0], args),
                    kwargs)).iteritems():
            proc.bind(k, v)

        proc.run()

        stack.pop()
        return proc.get_last_outputs()

    return wrapped_function


def aiidise(func):
    import inspect
    import itertools

    def wrapped_function(*args, **kwargs):
        in_dict = dict(
            itertools.chain(
                itertools.izip(inspect.getargspec(func)[0], args), kwargs))

        native_args = [util.to_native_type(arg) for arg in args]
        native_kwargs = {k: util.to_native_type(v) for k, v in kwargs.iteritems()}

        # Create the calculation (unstored)
        calc = Calculation()
        util.save_calc(calc, func, in_dict)

        # Run the wrapped function
        retval = util.to_db_type(func(*native_args, **native_kwargs))

        retval._add_link_from(calc, 'result')

        return retval

    return wrapped_function
