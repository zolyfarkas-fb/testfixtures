# Copyright (c) 2008-2011 Simplistix Ltd
# See license.txt for license details.

import sample1,sample2
from datetime import date
from datetime import datetime as d
from datetime import timedelta
from datetime import tzinfo
from time import strptime
from testfixtures import test_datetime,test_date
from testfixtures import replace, Replacer, compare, ShouldRaise
from unittest import TestCase,TestSuite,makeSuite

class TestTZInfo(tzinfo):

    def utcoffset(self, dt):
        return timedelta(minutes = 3) + self.dst(dt)

    def tzname(self, dt):
        return 'TestTZ'

    def dst(self, dt):
        return timedelta(minutes = 1)

class TestTZ2Info(tzinfo):

    def utcoffset(self, dt):
        return timedelta(minutes = 5)

    def tzname(self, dt):
        return 'TestTZ'

    def dst(self, dt):
        return timedelta(minutes = 0)

class TestDateTime(TestCase):

    @replace('datetime.datetime',test_datetime())
    def test_now(self):
        from datetime import datetime
        compare(datetime.now(),d(2001,1,1,0,0,0))
        compare(datetime.now(),d(2001,1,1,0,0,10))
        compare(datetime.now(),d(2001,1,1,0,0,30))

    @replace('datetime.datetime',test_datetime())
    def test_now_with_tz_supplied(self):
        from datetime import datetime
        info = TestTZInfo()
        compare(datetime.now(info),d(2001,1,1,0,4,tzinfo=TestTZInfo()))

    @replace('datetime.datetime',test_datetime(tzinfo=TestTZInfo()))
    def test_now_with_tz_setup(self):
        from datetime import datetime
        compare(datetime.now(),d(2001,1,1))

    @replace('datetime.datetime',test_datetime(tzinfo=TestTZInfo()))
    def test_now_with_tz_setup_and_supplied(self):
        from datetime import datetime
        info = TestTZ2Info()
        compare(datetime.now(info),d(2001,1,1,0,1,tzinfo=info))

    @replace('datetime.datetime',test_datetime(tzinfo=TestTZInfo()))
    def test_now_with_tz_setup_and_same_supplied(self):
        from datetime import datetime
        info = TestTZInfo()
        compare(datetime.now(info),d(2001,1,1,tzinfo=info))

    @replace('datetime.datetime',test_datetime(2002,1,1,1,2,3))
    def test_now_supplied(self):
        from datetime import datetime
        compare(datetime.now(),d(2002,1,1,1,2,3))

    @replace('datetime.datetime',test_datetime(None))
    def test_now_sequence(self,t):
        t.add(2002,1,1,1,0,0)
        t.add(2002,1,1,2,0,0)
        t.add(2002,1,1,3,0,0)
        from datetime import datetime
        compare(datetime.now(),d(2002,1,1,1,0,0))
        compare(datetime.now(),d(2002,1,1,2,0,0))
        compare(datetime.now(),d(2002,1,1,3,0,0))

    @replace('datetime.datetime',test_datetime())
    def test_add_and_set(self,t):
        t.add(2002,1,1,1,0,0)
        t.add(2002,1,1,2,0,0)
        t.set(2002,1,1,3,0,0)
        from datetime import datetime
        compare(datetime.now(),d(2002,1,1,3,0,0))
        compare(datetime.now(),d(2002,1,1,3,0,10))
        compare(datetime.now(),d(2002,1,1,3,0,30))

    @replace('datetime.datetime',test_datetime(None))
    def test_add_datetime_supplied(self,t):
        from datetime import datetime
        t.add(d(2002,1,1,1))
        t.add(datetime(2002,1,1,2))
        compare(datetime.now(),d(2002,1,1,1,0,0))
        compare(datetime.now(),d(2002,1,1,2,0,0))
        with ShouldRaise(ValueError(
            'Cannot add datetime with tzinfo set'
            )):
            t.add(d(2001, 1, 1, tzinfo=TestTZInfo()))
            
    @replace('datetime.datetime',test_datetime(None))
    def test_now_requested_longer_than_supplied(self,t):
        t.add(2002,1,1,1,0,0)
        t.add(2002,1,1,2,0,0)
        from datetime import datetime
        compare(datetime.now(),d(2002,1,1,1,0,0))
        compare(datetime.now(),d(2002,1,1,2,0,0))
        compare(datetime.now(),d(2002,1,1,2,0,10))
        compare(datetime.now(),d(2002,1,1,2,0,30))

    @replace('datetime.datetime',test_datetime(strict=True))
    def test_call(self,t):
        compare(t(2002,1,2,3,4,5),d(2002,1,2,3,4,5))
        from datetime import datetime
        dt = datetime(2001,1,1,1,0,0)
        self.failIf(dt.__class__ is d)
        compare(dt,d(2001,1,1,1,0,0))
    
    def test_date_return_type(self):
        with Replacer() as r:
            r.replace('datetime.datetime',test_datetime())
            from datetime import datetime
            dt = datetime(2001,1,1,1,0,0)
            d = dt.date()
            compare(d,date(2001,1,1))
            self.failUnless(d.__class__ is date)
    
    def test_date_return_type_picky(self):
        # type checking is a bitch :-/
        date_type = test_date(strict=True)
        with Replacer() as r:
            r.replace('datetime.datetime',test_datetime(
                    date_type=date_type,
                    strict=True,
                    ))
            from datetime import datetime
            dt = datetime(2010,8,26,14,33,13)
            d = dt.date()
            compare(d,date_type(2010,8,26))
            self.failUnless(d.__class__ is date_type)
    
    # if you have an embedded `now` as above, *and* you need to supply
    # a list of required datetimes, then it's often simplest just to
    # do a manual try-finally with a replacer:
    def test_import_and_obtain_with_lists(self):
        
        t = test_datetime(None)
        t.add(2002,1,1,1,0,0)
        t.add(2002,1,1,2,0,0)

        from testfixtures import Replacer
        r = Replacer()
        r.replace('testfixtures.tests.sample1.now',t.now)
        try:
            compare(sample1.str_now_2(),'2002-01-01 01:00:00')
            compare(sample1.str_now_2(),'2002-01-01 02:00:00')
        finally:
            r.restore()
        
    @replace('datetime.datetime',test_datetime())
    def test_repr(self):
        from datetime import datetime
        compare(repr(datetime),"<class 'testfixtures.tdatetime.tdatetime'>")


    @replace('datetime.datetime',test_datetime(delta=1))
    def test_delta(self):
        from datetime import datetime
        compare(datetime.now(),d(2001,1,1,0,0,0))
        compare(datetime.now(),d(2001,1,1,0,0,1))
        compare(datetime.now(),d(2001,1,1,0,0,2))
        
    @replace('datetime.datetime',test_datetime(delta_type='minutes'))
    def test_delta_type(self):
        from datetime import datetime
        compare(datetime.now(),d(2001,1,1,0,0,0))
        compare(datetime.now(),d(2001,1,1,0,10,0))
        compare(datetime.now(),d(2001,1,1,0,30,0))
        
    @replace('datetime.datetime',test_datetime(None))
    def test_set(self):
        from datetime import datetime
        datetime.set(2001,1,1,1,0,1)
        compare(datetime.now(),d(2001,1,1,1,0,1))
        datetime.set(2002,1,1,1,0,0)
        compare(datetime.now(),d(2002,1,1,1,0,0))
        compare(datetime.now(),d(2002,1,1,1,0,20))
        
    @replace('datetime.datetime',test_datetime(None))
    def test_set_datetime_supplied(self,t):
        from datetime import datetime
        t.set(d(2002,1,1,1))
        compare(datetime.now(),d(2002,1,1,1,0,0))
        t.set(datetime(2002,1,1,2))
        compare(datetime.now(),d(2002,1,1,2,0,0))
        with ShouldRaise(ValueError(
            'Cannot set datetime with tzinfo set'
            )):
            t.set(d(2001, 1, 1, tzinfo=TestTZInfo()))
            
    @replace('datetime.datetime',test_datetime(None,tzinfo=TestTZInfo()))
    def test_set_tz_setup(self):
        from datetime import datetime
        datetime.set(year=2002,month=1,day=1)
        compare(datetime.now(),d(2002,1,1))
        
    @replace('datetime.datetime',test_datetime(None))
    def test_set_kw(self):
        from datetime import datetime
        datetime.set(year=2002,month=1,day=1)
        compare(datetime.now(),d(2002,1,1))
        
    @replace('datetime.datetime',test_datetime(None))
    def test_set_tzinfo_kw(self):
        from datetime import datetime
        with ShouldRaise(TypeError('Cannot set tzinfo on tdatetime')):
            datetime.set(year=2002,month=1,day=1,tzinfo=TestTZInfo())
        
    @replace('datetime.datetime',test_datetime(None))
    def test_set_tzinfo_args(self):
        from datetime import datetime
        with ShouldRaise(TypeError('Cannot set tzinfo on tdatetime')):
            datetime.set(2002,1,2,3,4,5,6,TestTZInfo())
        
    @replace('datetime.datetime',test_datetime(None))
    def test_add_kw(self,t):
        from datetime import datetime
        t.add(year=2002,day=1,month=1)
        compare(datetime.now(),d(2002,1,1))
        
    @replace('datetime.datetime',test_datetime(None))
    def test_add_tzinfo_kw(self,t):
        from datetime import datetime
        with ShouldRaise(TypeError('Cannot add tzinfo to tdatetime')):
            datetime.add(year=2002,month=1,day=1,tzinfo=TestTZInfo())
        
    @replace('datetime.datetime',test_datetime(None))
    def test_add_tzinfo_args(self,t):
        from datetime import datetime
        with ShouldRaise(TypeError('Cannot add tzinfo to tdatetime')):
            datetime.add(2002,1,2,3,4,5,6,TestTZInfo())
        
    @replace('datetime.datetime',test_datetime(2001,1,2,3,4,5,6,TestTZInfo()))
    def test_max_number_args(self):
        from datetime import datetime
        compare(datetime.now(),d(2001,1,2,3,4,5,6))
        
    @replace('datetime.datetime',test_datetime(2001,1,2))
    def test_min_number_args(self):
        from datetime import datetime
        compare(datetime.now(),d(2001,1,2))

    @replace('datetime.datetime',test_datetime(
        year=2001,
        month=1,
        day=2,
        hour=3,
        minute=4,
        second=5,
        microsecond=6,
        tzinfo=TestTZInfo()
        ))
    def test_all_kw(self):
        from datetime import datetime
        compare(datetime.now(),d(2001,1,2,3,4,5,6))
        
    @replace('datetime.datetime',test_datetime(2001,1,2))
    def test_utc_now(self):
        from datetime import datetime
        compare(datetime.utcnow(),d(2001,1,2))
        
    @replace('datetime.datetime',
             test_datetime(2001, 1, 2, tzinfo=TestTZInfo()))
    def test_utc_now_with_tz(self):
        from datetime import datetime
        compare(datetime.utcnow(),d(2001, 1, 1, 23, 56))
        
    @replace('datetime.datetime', test_datetime(strict=True))
    def test_isinstance_strict(self):
        from datetime import datetime
        to_check = []
        to_check.append(datetime(1999, 1, 1))
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
        to_check.append(datetime.utcnow())
        datetime.set(2001, 1, 1, 20)
        to_check.append(datetime.now())
        datetime.add(2001, 1, 1, 21)
        to_check.append(datetime.now())
        to_check.append(datetime.now())
        datetime.set(datetime(2001, 1, 1, 22))
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
        datetime.add(datetime(2001, 1, 1, 23))
        to_check.append(datetime.now())
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
        datetime.set(d(2001, 1, 1, 22))
        to_check.append(datetime.now())
        datetime.add(d(2001, 1, 1, 23))
        to_check.append(datetime.now())
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
                     
        for inst in to_check:
            self.failUnless(isinstance(inst, datetime), inst)
            self.failUnless(inst.__class__ is datetime, inst)
            self.failUnless(isinstance(inst, d), inst)
            self.failIf(inst.__class__ is d, inst)
            
    @replace('datetime.datetime', test_datetime())
    def test_isinstance_default(self):
        from datetime import datetime
        to_check = []
        to_check.append(datetime(1999, 1, 1))
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
        to_check.append(datetime.utcnow())
        datetime.set(2001, 1, 1, 20)
        to_check.append(datetime.now())
        datetime.add(2001, 1, 1, 21)
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
        datetime.set(datetime(2001, 1, 1, 22))
        to_check.append(datetime.now())
        datetime.add(datetime(2001, 1, 1, 23))
        to_check.append(datetime.now())
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
        datetime.set(d(2001, 1, 1, 22))
        to_check.append(datetime.now())
        datetime.add(d(2001, 1, 1, 23))
        to_check.append(datetime.now())
        to_check.append(datetime.now())
        to_check.append(datetime.now(TestTZInfo()))
                     
        for inst in to_check:
            self.failIf(isinstance(inst, datetime), inst)
            self.failIf(inst.__class__ is datetime, inst)
            self.failUnless(isinstance(inst, d), inst)
            self.failUnless(inst.__class__ is d, inst)

def test_suite():
    return TestSuite((
        makeSuite(TestDateTime),
        ))
