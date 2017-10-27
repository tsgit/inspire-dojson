# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import pytest

from flask import current_app
from mock import patch

from inspire_dojson.utils import (
    absolute_url,
    normalize_rank,
    force_single_element,
    get_recid_from_ref,
    get_record_ref,
    legacy_export_as_marc,
    dedupe_all_lists,
    strip_empty_values,
    normalize_date_aggressively,
)


def test_normalize_rank_returns_none_on_falsy_value():
    assert normalize_rank('') is None


def test_normalize_rank_returns_uppercase_value_if_found_in_rank_types():
    expected = 'STAFF'
    result = normalize_rank('staff')

    assert expected == result


def test_normalize_rank_ignores_periods_in_value():
    expected = 'PHD'
    result = normalize_rank('Ph.D.')

    assert expected == result


def test_normalize_rank_allows_alternative_names():
    expected = 'VISITOR'
    result = normalize_rank('VISITING SCIENTIST')

    assert expected == result


def test_normalize_rank_allows_abbreviations():
    expected = 'POSTDOC'
    result = normalize_rank('PD')

    assert expected == result


def test_normalize_rank_falls_back_on_other():
    expected = 'OTHER'
    result = normalize_rank('FOO')

    assert expected == result


def test_force_single_element_returns_first_element_on_a_list():
    expected = 'foo'
    result = force_single_element(['foo', 'bar', 'baz'])

    assert expected == result


def test_force_single_element_returns_element_when_not_a_list():
    expected = 'foo'
    result = force_single_element('foo')

    assert expected == result


def test_force_single_element_returns_none_on_empty_list():
    assert force_single_element([]) is None


def test_absolute_url_with_empty_server_name():
    config = {}

    with patch.dict(current_app.config, config, clear=True):
        expected = 'http://inspirehep.net/foo'
        result = absolute_url('foo')

        assert expected == result


def test_absolute_url_with_server_name_localhost():
    config = {'SERVER_NAME': 'localhost:5000'}

    with patch.dict(current_app.config, config):
        expected = 'http://localhost:5000/foo'
        result = absolute_url('foo')

        assert expected == result


def test_absolute_url_with_http_server_name():
    config = {'SERVER_NAME': 'http://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'http://example.com/foo'
        result = absolute_url('foo')

        assert expected == result


def test_absolute_url_with_https_server_name():
    config = {'SERVER_NAME': 'https://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'https://example.com/foo'
        result = absolute_url('foo')

        assert expected == result


def test_get_record_ref_with_empty_server_name():
    config = {}

    with patch.dict(current_app.config, config, clear=True):
        expected = 'http://inspirehep.net/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_with_server_name_localhost():
    config = {'SERVER_NAME': 'localhost:5000'}

    with patch.dict(current_app.config, config):
        expected = 'http://localhost:5000/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_with_http_server_name():
    config = {'SERVER_NAME': 'http://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'http://example.com/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_with_https_server_name():
    config = {'SERVER_NAME': 'https://example.com'}

    with patch.dict(current_app.config, config):
        expected = 'https://example.com/api/endpoint/123'
        result = get_record_ref(123, 'endpoint')

        assert expected == result['$ref']


def test_get_record_ref_without_recid_returns_none():
    assert get_record_ref(None, 'endpoint') is None


def test_get_record_ref_without_endpoint_defaults_to_record():
    config = {}

    with patch.dict(current_app.config, config, clear=True):
        expected = 'http://inspirehep.net/api/record/123'
        result = get_record_ref(123)

        assert expected == result['$ref']


def test_get_recid_from_ref_returns_none_on_none():
    assert get_recid_from_ref(None) is None


def test_get_recid_from_ref_returns_none_on_simple_strings():
    assert get_recid_from_ref('a_string') is None


def test_get_recid_from_ref_returns_none_on_empty_object():
    assert get_recid_from_ref({}) is None


def test_get_recid_from_ref_returns_none_on_object_with_wrong_key():
    assert get_recid_from_ref({'bad_key': 'some_val'}) is None


def test_get_recid_from_ref_returns_none_on_ref_a_simple_string():
    assert get_recid_from_ref({'$ref': 'a_string'}) is None


def test_get_recid_from_ref_returns_none_on_ref_malformed():
    assert get_recid_from_ref({'$ref': 'http://bad_url'}) is None


def test_legacy_export_as_marc_empty_json():
    empty_json = {}

    expected = '<record>\n</record>\n'
    result = legacy_export_as_marc(empty_json)

    assert expected == result


def test_legacy_export_as_marc_falsy_value():
    falsy_value = {'001': ''}

    expected = '<record>\n</record>\n'
    result = legacy_export_as_marc(falsy_value)

    assert expected == result


def test_legacy_export_as_marc_json_with_controlfield():
    json_with_controlfield = {'001': '4328'}

    expected = (
        '<record>\n'
        '    <controlfield tag="001">4328</controlfield>\n'
        '</record>\n'
    )
    result = legacy_export_as_marc(json_with_controlfield)

    assert expected == result


def test_legacy_export_as_marc_handles_unicode():
    record = {
        '100': [
            {'a': u'Kätlne, J.'},
        ],
    }

    expected = (
        u'<record>\n'
        u'    <datafield tag="100" ind1="" ind2="">\n'
        u'        <subfield code="a">Kätlne, J.</subfield>\n'
        u'    </datafield>\n'
        u'</record>\n'
    )
    result = legacy_export_as_marc(record)

    assert expected == result


def test_legacy_export_as_marc_handles_numbers():
    record = {
        '773': [
            {'y': 1975},
        ],
    }

    expected = (
        '<record>\n'
        '    <datafield tag="773" ind1="" ind2="">\n'
        '        <subfield code="y">1975</subfield>\n'
        '    </datafield>\n'
        '</record>\n'
    )
    result = legacy_export_as_marc(record)

    assert expected == result


def test_dedupe_all_lists():
    obj = {'l0': list(range(10)) + list(range(10)),
           'o1': [{'foo': 'bar'}] * 10,
           'o2': [{'foo': [1, 2]}, {'foo': [1, 1, 2]}] * 10}

    expected = {'l0': list(range(10)),
                'o1': [{'foo': 'bar'}],
                'o2': [{'foo': [1, 2]}]}

    assert dedupe_all_lists(obj) == expected


def test_strip_empty_values():
    obj = {
        '_foo': (),
        'foo': (1, 2, 3),
        '_bar': [],
        'bar': [1, 2, 3],
        '_baz': set(),
        'baz': set([1, 2, 3]),
        'qux': True,
        'quux': False,
        'plugh': 0,
    }

    expected = {
        'foo': (1, 2, 3),
        'bar': [1, 2, 3],
        'baz': set([1, 2, 3]),
        'qux': True,
        'quux': False,
        'plugh': 0,
    }
    result = strip_empty_values(obj)

    assert expected == result


def test_strip_empty_values_returns_none_on_none():
    assert strip_empty_values(None) is None


def test_normalize_date_aggressively_accepts_correct_date():
    assert normalize_date_aggressively('2015-02-24') == '2015-02-24'


def test_normalize_date_aggressively_strips_wrong_day():
    assert normalize_date_aggressively('2015-02-31') == '2015-02'


def test_normalize_date_aggressively_strips_wrong_month():
    assert normalize_date_aggressively('2015-20-24') == '2015'


def test_normalize_date_aggressively_raises_on_wrong_format():
    with pytest.raises(ValueError):
        normalize_date_aggressively('2014=12-01')


def test_normalize_date_aggressively_ignores_fake_dates():
        assert normalize_date_aggressively('0000') is None
