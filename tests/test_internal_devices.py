from __future__ import (
    unicode_literals,
    absolute_import,
    print_function,
    division,
    )
str = type('')

import warnings
from mock import patch
import io
import errno
from subprocess import CalledProcessError

import pytest

from gpiozero import *
from datetime import datetime, time

file_not_found = IOError(errno.ENOENT, 'File not found')
bad_ping = CalledProcessError(1, 'returned non-zero exit status 1')

def test_timeofday_bad_init():
    with pytest.raises(TypeError):
         TimeOfDay()
    with pytest.raises(ValueError):
        TimeOfDay(7, 12)
    with pytest.raises(TypeError):
        TimeOfDay(time(7))
    with pytest.raises(ValueError):
        TimeOfDay(time(7), time(7))
    with pytest.raises(ValueError):
        TimeOfDay(time(7), time(7))
    with pytest.raises(ValueError):
        TimeOfDay('7:00', '8:00')
    with pytest.raises(ValueError):
        TimeOfDay(7.00, 8.00)
    with pytest.raises(ValueError):
        TimeOfDay(datetime(2019, 1, 24, 19), time(19))  # lurch edge case

def test_timeofday_init():
    TimeOfDay(time(7), time(8), utc=False)
    TimeOfDay(time(7), time(8), utc=True)
    TimeOfDay(time(0), time(23, 59))
    TimeOfDay(time(0), time(23, 59))
    TimeOfDay(time(12, 30), time(13, 30))
    TimeOfDay(time(23), time(1))
    TimeOfDay(time(6), time(18))
    TimeOfDay(time(18), time(6))
    TimeOfDay(datetime(2019, 1, 24, 19), time(19, 1))  # lurch edge case

def test_timeofday_value():
    with TimeOfDay(time(7), time(8), utc=False) as tod:
        assert tod.start_time == time(7)
        assert tod.end_time == time(8)
        assert not tod.utc
        with patch('gpiozero.internal_devices.datetime') as dt:
            dt.now.return_value = datetime(2018, 1, 1, 6, 59, 0)
            assert not tod.is_active
            dt.now.return_value = datetime(2018, 1, 1, 7, 0, 0)
            assert tod.is_active
            dt.now.return_value = datetime(2018, 1, 2, 8, 0, 0)
            assert tod.is_active
            dt.now.return_value = datetime(2018, 1, 2, 8, 1, 0)
            assert not tod.is_active

    with TimeOfDay(time(1, 30), time(23, 30)) as tod:
        assert tod.start_time == time(1, 30)
        assert tod.end_time == time(23, 30)
        assert tod.utc
        with patch('gpiozero.internal_devices.datetime') as dt:
            dt.utcnow.return_value = datetime(2018, 1, 1, 1, 29, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 1, 30, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 12, 30, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 23, 30, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 23, 31, 0)
            assert not tod.is_active

    with TimeOfDay(time(23), time(1)) as tod:
        with patch('gpiozero.internal_devices.datetime') as dt:
            dt.utcnow.return_value = datetime(2018, 1, 1, 22, 59, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 23, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 1, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 1, 1, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 3, 12, 0, 0)
            assert not tod.is_active

    with TimeOfDay(time(6), time(5)) as tod:
        with patch('gpiozero.internal_devices.datetime') as dt:
            dt.utcnow.return_value = datetime(2018, 1, 1, 5, 30, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 5, 59, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 6, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 18, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 1, 5, 0, 0)
            assert tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 5, 1, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 5, 30, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 5, 59, 0)
            assert not tod.is_active
            dt.utcnow.return_value = datetime(2018, 1, 2, 6, 0, 0)
            assert tod.is_active

def test_pingserver_bad_init():
    with pytest.raises(TypeError):
         PingServer()

def test_pingserver_init():
    with patch('gpiozero.internal_devices.subprocess') as sp:
        sp.check_call.return_value = True
        with PingServer('example.com') as server:
            assert server.host == 'example.com'
        with PingServer('192.168.1.10') as server:
            assert server.host == '192.168.1.10'
        with PingServer('8.8.8.8') as server:
            assert server.host == '8.8.8.8'
        with PingServer('2001:4860:4860::8888') as server:
            assert server.host == '2001:4860:4860::8888'

def test_pingserver_value():
    with patch('gpiozero.internal_devices.subprocess.check_call') as check_call:
        with PingServer('example.com') as server:
            assert server.is_active
            check_call.side_effect = bad_ping
            assert not server.is_active
            check_call.side_effect = None
            assert server.is_active

def test_cputemperature_bad_init():
    with patch('io.open') as m:
        m.return_value.__enter__.side_effect = file_not_found
        with pytest.raises(IOError):
            with CPUTemperature('') as temp:
                temp.value
        with pytest.raises(IOError):
            with CPUTemperature('badfile') as temp:
                temp.value
        m.return_value.__enter__.return_value.readline.return_value = '37000'
        with pytest.raises(ValueError):
            CPUTemperature(min_temp=100)
        with pytest.raises(ValueError):
            CPUTemperature(min_temp=10, max_temp=10)
        with pytest.raises(ValueError):
            CPUTemperature(min_temp=20, max_temp=10)

def test_cputemperature():
    with patch('io.open') as m:
        m.return_value.__enter__.return_value.readline.return_value = '37000'
        with CPUTemperature() as cpu:
            assert cpu.temperature == 37.0
            assert cpu.value == 0.37
        with warnings.catch_warnings(record=True) as w:
            with CPUTemperature(min_temp=30, max_temp=40) as cpu:
                assert cpu.value == 0.7
                assert not cpu.is_active
            assert len(w) == 1
            assert w[0].category == ThresholdOutOfRange
            assert cpu.temperature == 37.0
        with CPUTemperature(min_temp=30, max_temp=40, threshold=35) as cpu:
            assert cpu.is_active

def test_loadaverage_bad_init():
    with patch('io.open') as m:
        foo = m.return_value.__enter__
        foo.side_effect = file_not_found
        with pytest.raises(IOError):
            with LoadAverage('') as load:
                load.value
        with pytest.raises(IOError):
            with LoadAverage('badfile') as load:
                load.value
        foo.return_value.readline.return_value = '0.09 0.10 0.09 1/292 20758'
        with pytest.raises(ValueError):
            LoadAverage(min_load_average=1)
        with pytest.raises(ValueError):
            LoadAverage(min_load_average=0.5, max_load_average=0.5)
        with pytest.raises(ValueError):
            LoadAverage(min_load_average=1, max_load_average=0.5)
        with pytest.raises(ValueError):
            LoadAverage(minutes=0)
        with pytest.raises(ValueError):
            LoadAverage(minutes=10)

def test_loadaverage():
    with patch('io.open') as m:
        foo = m.return_value.__enter__
        foo.return_value.readline.return_value = '0.09 0.10 0.09 1/292 20758'
        with LoadAverage() as la:
            assert la.min_load_average == 0
            assert la.max_load_average == 1
            assert la.threshold == 0.8
            assert la.load_average == 0.1
            assert la.value == 0.1
            assert not la.is_active
        foo.return_value.readline.return_value = '1.72 1.40 1.31 3/457 23102'
        with LoadAverage(min_load_average=0.5, max_load_average=2,
                         threshold=1, minutes=5) as la:
            assert la.min_load_average == 0.5
            assert la.max_load_average == 2
            assert la.threshold == 1
            assert la.load_average == 1.4
            assert la.value == 0.6
            assert la.is_active
        with warnings.catch_warnings(record=True) as w:
            with LoadAverage(min_load_average=1, max_load_average=2,
                         threshold=0.8, minutes=5) as la:
                assert len(w) == 1
                assert w[0].category == ThresholdOutOfRange
                assert la.load_average == 1.4
