'''
Created on Nov 12, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''

import sys
import os
import time
import logging
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from nsts.profiles.base import ExecutionDirection, ResultValueDescriptor, \
    ProfileExecutor, Profile, ProfileExecution
from nsts import units
from nsts.options import Options, OptionsDescriptor
from nsts.proto import NSTSConnection, Message, ProtocolError
import socket
from collections import deque


class ProfileExecutorA(ProfileExecutor):
    pass


class ProfileExecutorB(ProfileExecutor):
    pass


class NullNSTSConnection(NSTSConnection):

    def __init__(self):
        super(NullNSTSConnection, self).__init__(socket.socket())
        self.queue = deque()

    def send_msg(self, msg_type, msg_params={}):
        self.queue.appendleft(Message(msg_type, msg_params))

    def wait_msg(self):
        return self.queue.pop()


class TestExecutionDirection(unittest.TestCase):

    def test_constructor(self):

        # Check empty constructor
        with self.assertRaises(TypeError):
            ExecutionDirection()

        # Check wrong names
        with self.assertRaises(ValueError):
            ExecutionDirection("la")

        with self.assertRaises(ValueError):
            ExecutionDirection("sen")

        with self.assertRaises(ValueError):
            ExecutionDirection("rec")

        # Valid constructors
        ExecutionDirection("s")
        ExecutionDirection("send")
        ExecutionDirection("r")
        ExecutionDirection("receive")

    def test_is_func(self):
        d = ExecutionDirection("s")
        self.assertTrue(d.is_send())
        self.assertFalse(d.is_receive())
        d = ExecutionDirection("s")
        self.assertTrue(d.is_send())
        self.assertFalse(d.is_receive())

        d = ExecutionDirection("r")
        self.assertFalse(d.is_send())
        self.assertTrue(d.is_receive())
        d = ExecutionDirection("receive")
        self.assertFalse(d.is_send())
        self.assertTrue(d.is_receive())

    def test_opposite(self):
        d = ExecutionDirection("s")
        o = d.opposite()

        self.assertIsInstance(o, ExecutionDirection)
        self.assertFalse(o.is_send())
        self.assertTrue(o.is_receive())

        d = ExecutionDirection("r")
        o = d.opposite()

        self.assertIsInstance(o, ExecutionDirection)
        self.assertTrue(o.is_send())
        self.assertFalse(o.is_receive())


class TestResultValueDescriptor(unittest.TestCase):

    def test_constructor(self):
        # Cannot omit parameters
        with self.assertRaises(TypeError):
            ResultValueDescriptor()

        # Assert on types
        with self.assertRaises(TypeError):
            ResultValueDescriptor('a', 'a', float)

        ResultValueDescriptor('myid', 'myname', units.Time)
        ResultValueDescriptor(1, '', units.BitRate)

    def test_properties(self):

        r = ResultValueDescriptor('myid', 'myname', units.Time)
        self.assertEqual(r.id, 'myid')
        self.assertEqual(r.name, 'myname')
        self.assertEqual(r.unit_type, units.Time)

        r = ResultValueDescriptor(1, '', units.BitRate)
        self.assertEqual(r.id, 1)
        self.assertEqual(r.name, '')
        self.assertEqual(r.unit_type, units.BitRate)


class TestProfileExecutor(unittest.TestCase):

    def dummy_ctx(self):
        p = Profile('profid', 'profame', ProfileExecutor, ProfileExecutor)
        c = NullNSTSConnection()
        ctx = ProfileExecution(p, ExecutionDirection('s'),
                               Options(p.supported_options), c)
        return ctx

    def test_constructor(self):

        # Cannot omit parameters
        with self.assertRaises(TypeError):
            ProfileExecutor()

        ProfileExecutor(self.dummy_ctx())
        with self.assertRaises(TypeError):
            ProfileExecutor(1)

    def test_properties(self):

        ctx = self.dummy_ctx()
        e = ProfileExecutor(ctx)

        self.assertEqual(e.context, ctx)
        self.assertEqual(e.profile, ctx.profile)
        self.assertEquals(len(e.results), 0)

        self.assertIsInstance(e.logger, logging.Logger)
        self.assertEqual("profile.profid", e.logger.name)

    def test_store_result(self):
        ctx = self.dummy_ctx()
        e = ProfileExecutor(ctx)

        with self.assertRaises(ValueError):
            e.store_result('smt', 'a')

        ctx.profile.add_result('smt', 'Something', units.Time)
        ctx.profile.add_result('smt2', 'Something', units.Time)
        ctx.profile.add_result('smt3', 'Something', units.Time)

        e = ProfileExecutor(ctx)
        self.assertEqual(len(e.results), 3)
        self.assertIsNone(e.results['smt'])
        self.assertIsNone(e.results['smt2'])
        self.assertIsNone(e.results['smt3'])

        # Check casting for storing
        e.store_result('smt', 0)
        self.assertEqual(e.results['smt'], units.Time(0))

        # Overwrite values
        e.store_result('smt', '15 hour')
        self.assertNotEqual(e.results['smt'], units.Time(0))
        self.assertEqual(e.results['smt'], units.Time('15 hour'))

    def test_result_order(self):
        ctx = self.dummy_ctx()
        p = ctx.profile
        p.add_result('smt1', 'Something', units.Time)
        p.add_result('smt2', 'Something', units.Time)
        p.add_result('smt3', 'Something', units.Time)
        e = ProfileExecutor(ctx)

        # Check order
        self.assertEqual(['smt1', 'smt2', 'smt3'], e.results.keys())

        ctx = self.dummy_ctx()
        p = ctx.profile
        p.add_result('smt3', 'Something', units.Time)
        p.add_result('smt2', 'Something', units.Time)
        p.add_result('smt1', 'Something', units.Time)
        e = ProfileExecutor(ctx)

        # Check order
        self.assertEqual(['smt3', 'smt2', 'smt1'], e.results.keys())

    def test_unimplemented(self):
        e = ProfileExecutor(self.dummy_ctx())

        with self.assertRaises(NotImplementedError):
            e.prepare()

        with self.assertRaises(NotImplementedError):
            e.is_supported()

        with self.assertRaises(NotImplementedError):
            e.run()

        with self.assertRaises(NotImplementedError):
            e.cleanup()

    def test_msg(self):
        p = Profile('profid', 'profname', ProfileExecutorA, ProfileExecutorB)
        c = NullNSTSConnection()
        ctxa = ProfileExecution(p, ExecutionDirection('s'),
                                Options(p.supported_options), c)
        a = ctxa.executor
        ctxb = ProfileExecution(p, ExecutionDirection('r'),
                                Options(p.supported_options), c)
        b = ctxb.executor

        a.send_msg('LALA')
        msg = b.wait_msg_type('LALA')
        self.assertEqual(msg.type, '__profid_LALA')
        self.assertEqual(msg.params, {})

        a.send_msg('LALA2')
        with self.assertRaises(ProtocolError):
            msg = b.wait_msg_type('LALA')

    def test_propage_results(self):
        p = Profile('profid', 'profname', ProfileExecutorA, ProfileExecutorB)
        p.add_result('testdt', 'name', units.Time)
        p.add_result('testbit', 'name', units.BitRate)

        c = NullNSTSConnection()
        ctxa = ProfileExecution(p, ExecutionDirection('s'),
                                Options(p.supported_options), c)
        a = ctxa.executor
        ctxb = ProfileExecution(p, ExecutionDirection('r'),
                                Options(p.supported_options), c)
        b = ctxb.executor

        a.store_result('testdt', '10 sec')
        a.store_result('testbit', '32 bps')
        a.propagate_results()

        b.collect_results()
        self.assertEqual(b.results['testdt'], units.Time('10 sec'))
        self.assertEqual(b.results['testbit'], units.BitRate('32 bps'))


class TestProfile(unittest.TestCase):

    def test_constructor(self):
        with self.assertRaises(TypeError):
            Profile()

        with self.assertRaises(TypeError):
            Profile('myid', 'myname', ProfileExecutor, float)

        with self.assertRaises(TypeError):
            Profile('myid', 'myname', float, ProfileExecutor)

        Profile('myid', 'myname', ProfileExecutor, ProfileExecutor)

    def test_properties(self):
        d = Profile('myid', 'myname', ProfileExecutorA, ProfileExecutorB)
        self.assertEqual(d.id, 'myid')
        self.assertEqual(d.name, 'myname')
        self.assertEqual(d.send_executor_class, ProfileExecutorA)
        self.assertEqual(d.receive_executor_class, ProfileExecutorB)
        self.assertIsNotNone(d.supported_options)
        self.assertIsNotNone(d.supported_results)
        self.assertIsNone(d.description)

        d = Profile('myid', 'myname', ProfileExecutorA,
                    ProfileExecutorB, description='mydesc')
        self.assertEqual(d.description, 'mydesc')

    def test_options(self):
        p = Profile('myid', 'myname', ProfileExecutorA, ProfileExecutorB)

        self.assertEqual(len(p.supported_options), 0)
        p.supported_options.add_option('myid', 'myhelp', float)
        self.assertEqual(p.supported_options['myid'].help, 'myhelp')

        # No need check as it is of type OptionsDescriptor
        self.assertIsInstance(p.supported_options, OptionsDescriptor)


class TestProfileExecution(unittest.TestCase):

    def test_constructor(self):
        p = Profile('myid', 'myname', ProfileExecutorA, ProfileExecutorB)
        dir = ExecutionDirection('s')
        with self.assertRaises(TypeError):
            ProfileExecution()

        with self.assertRaises(TypeError):
            ProfileExecution(p)

        with self.assertRaises(TypeError):
            ProfileExecution(p, dir)

        with self.assertRaises(TypeError):
            ProfileExecution(p, dir, Options(p.supported_options))

        c = NullNSTSConnection()

        with self.assertRaises(TypeError):
            ProfileExecution(p, dir, Options(p.supported_options), float)

        with self.assertRaises(TypeError):
            ProfileExecution(p, dir, float, c)

        with self.assertRaises(TypeError):
            ProfileExecution(p, float, Options(p.supported_options), c)

        with self.assertRaises(TypeError):
            ProfileExecution(float, dir, Options(p.supported_options), c)

        ctx = ProfileExecution(p, dir, Options(p.supported_options), c)

    def test_properties(self):
        c = NullNSTSConnection()
        p = Profile('myid', 'myname', ProfileExecutorA, ProfileExecutorB)
        dir = ExecutionDirection('s')
        opt = Options(p.supported_options)
        ctx = ProfileExecution(p, dir, opt, c)

        self.assertEqual(ctx.profile, p)
        self.assertEqual(ctx.connection, c)
        self.assertEqual(ctx.direction, dir)
        self.assertEqual(ctx.options, opt)

    def test_name(self):
        c = NullNSTSConnection()
        p = Profile('myid', 'myname', ProfileExecutorA, ProfileExecutorB)
        dir = ExecutionDirection('s')
        opt = Options(p.supported_options)
        ctx = ProfileExecution(p, dir, opt, c)
        self.assertIsInstance(ctx.name, basestring)

        self.assertTrue(p.name in ctx.name)

    def test_executor(self):
        c = NullNSTSConnection()
        p = Profile('myid', 'myname', ProfileExecutorA, ProfileExecutorB)
        opt = Options(p.supported_options)
        ctx = ProfileExecution(p, ExecutionDirection('s'), opt, c)

        x = ctx.executor
        self.assertIsInstance(x, ProfileExecutorA)
        self.assertEqual(x.profile, p)

        ctx = ProfileExecution(p, ExecutionDirection('r'), opt, c)
        x = ctx.executor
        self.assertIsInstance(x, ProfileExecutorB)
        self.assertEqual(x.profile, p)

    def test_finished(self):
        c = NullNSTSConnection()
        p = Profile('myid', 'myname', ProfileExecutorA, ProfileExecutorB)
        opt = Options(p.supported_options)
        ctx = ProfileExecution(p, ExecutionDirection('s'), opt, c)
        time.sleep(0.8)
        ctx.mark_finished()

        passed = ctx.execution_time()
        self.assertTrue(abs(passed.raw_value - 0.8) < 0.1)
