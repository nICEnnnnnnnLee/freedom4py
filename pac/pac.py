#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Source from https://github.com/carsonyl/pypac/blob/master/pypac/parser.py
Apache License Version 2.0

changes:
    from pypac.pyparser_functions  ... ->   from pyparser_functions
    delete class-PAC-unrelated functions
    if dukpy is not installed, just give a warning and return DIRECT
'''

"""
Functions and classes for parsing and executing PAC files.
"""

from pac.parser_functions import function_injections
try:
    import warnings
    import dukpy
    dukpyInstalled = True
except:
    import warnings
    warnings.warn("dukpy not installed, all result will set to DIRECT;")
    dukpyInstalled = False


def _inject_function_into_js(context, name, func):
    """
    Inject a Python function into the global scope of a dukpy JavaScript interpreter context.
    :type context: dukpy.JSInterpreter
    :param name: Name to give the function in JavaScript.
    :param func: Python function.
    """
    context.export_function(name, func)
    context.evaljs(
        """;
        {name} = function() {{
            var args = Array.prototype.slice.call(arguments);
            args.unshift('{name}');
            return call_python.apply(null, args);
        }};
    """.format(
            name=name
        )
    )


if dukpyInstalled:
    class PACFile(object):
        """
        Represents a PAC file.
        JavaScript parsing and execution is handled by the `dukpy`_ library.
        .. _dukpy: https://github.com/amol-/dukpy
        """

        def __init__(self, pac_js, **kwargs):
            """
            Load a PAC file from a given string of JavaScript.
            Errors during parsing and validation may raise a specialized exception.
            :param str pac_js: JavaScript that defines the FindProxyForURL() function.
            :raises MalformedPacError: If the JavaScript could not be parsed, does not define FindProxyForURL(),
                or is otherwise invalid.
            """
            if kwargs.get("recursion_limit"):
                import warnings
                warnings.warn(
                    "recursion_limit is deprecated and has no effect. It will be removed in a future release.")

            try:
                self._context = dukpy.JSInterpreter()
                for name, func in function_injections.items():
                    _inject_function_into_js(self._context, name, func)
                self._context.evaljs(pac_js)

                # A test call to weed out errors like unimplemented functions.
                self.find_proxy_for_url("/", "0.0.0.0")

            except dukpy.JSRuntimeError as e:
                raise MalformedPacError(original_exc=e)  # from e

        def find_proxy_for_url(self, url, host):
            """
            Call ``FindProxyForURL()`` in the PAC file with the given arguments.
            :param str url: The full URL.
            :param str host: The URL's host.
            :return: Result of evaluating the ``FindProxyForURL()`` JavaScript function in the PAC file.
            :rtype: str
            """
            return self._context.evaljs("FindProxyForURL(dukpy['url'], dukpy['host'])", url=url, host=host)
else:
    class PACFile(object):
        def __init__(self, pac_js, **kwargs):
            pass

        def find_proxy_for_url(self, url, host):
            return "DIRECT;"


class MalformedPacError(Exception):
    def __init__(self, msg=None, original_exc=None):
        if not msg:
            msg = "Malformed PAC file"
        self.original_exc = original_exc
        if original_exc:
            msg += " ({})".format(original_exc)
        super(MalformedPacError, self).__init__(msg)


class PyimportError(MalformedPacError):
    def __init__(self):
        super(PyimportError, self).__init__(
            "PAC file contains pyimport statement. " "Ensure that the source of your PAC file is trustworthy"
        )
        import warnings
        warnings.warn(
            "PyimportError is deprecated and will be removed in a future release.")


class PacComplexityError(RuntimeError):
    def __init__(self):
        super(PacComplexityError, self).__init__(
            "Maximum recursion depth exceeded while parsing PAC file. " "Raise it using sys.setrecursionlimit()"
        )
        import warnings
        warnings.warn(
            "PacComplexityError is deprecated and will be removed in a future release.")


if __name__ == '__main__':
    with open('d:\Workspace\PythonWorkspace\proxy\gfw_pac', 'r') as f:
        pac_js = f.read()
        pac = PACFile(pac_js)
        # import time
        # start = int(time.time())
        # for i in range(1000):
        #     print(result)
        # end = int(time.time())
        # print(f'time used: {end - start}s')
        domains = [
            "www.google.com",
            "172.217.15.110",
            "github.com",
            "www.baidu.com",
            "220.181.38.148",
        ]
        for domain in domains:
            result = pac.find_proxy_for_url("/", domain)
            print(f'{domain} : {result}')
