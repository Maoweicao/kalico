# Tests for the toolhead step generation callbacks
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from klippy.toolhead import ToolHead


class _FakeTrapq:
    pass


def _make_toolhead():
    th = object.__new__(ToolHead)
    th.last_flush_time = 0.0
    th.print_time = 10.0
    th.kin_flush_delay = 0.100
    th.min_restart_time = 0.0
    th.clear_history_time = 0.0
    th.can_pause = True
    th.pre_step_gen_callbacks = []
    th.step_generators = []
    th.flush_trapqs = []
    th.all_mcus = []
    th.trapq_finalize_moves = lambda *args: None
    return th


######################################################################
# Registration
######################################################################


def test_register_pre_step_gen_callback():
    th = _make_toolhead()

    def cb(flush_time):
        pass

    th.register_pre_step_gen_callback(cb)
    assert th.pre_step_gen_callbacks == [cb]


def test_register_pre_step_gen_callback_is_idempotent():
    th = _make_toolhead()

    def cb(flush_time):
        pass

    th.register_pre_step_gen_callback(cb)
    th.register_pre_step_gen_callback(cb)
    assert len(th.pre_step_gen_callbacks) == 1


def test_unregister_pre_step_gen_callback():
    th = _make_toolhead()

    def cb(flush_time):
        pass

    th.register_pre_step_gen_callback(cb)
    th.unregister_pre_step_gen_callback(cb)
    assert th.pre_step_gen_callbacks == []


def test_unregister_an_unknown_callback_is_a_noop():
    th = _make_toolhead()

    def cb(flush_time):
        pass

    th.unregister_pre_step_gen_callback(cb)
    assert th.pre_step_gen_callbacks == []


######################################################################
# Ordering
######################################################################


def test_the_callback_runs_before_the_step_generators():
    # The callback lowers the stepper reference - the step generators have
    # to see the lowered reference, otherwise the correction is lost
    th = _make_toolhead()
    order = []

    def pre_cb(flush_time):
        order.append("pre")

    def step_gen(flush_time):
        order.append("step")

    th.register_pre_step_gen_callback(pre_cb)
    th.step_generators.append(step_gen)
    th._advance_flush_time(9.0)
    assert order == ["pre", "step"]


def test_the_callback_receives_the_flush_time():
    th = _make_toolhead()
    seen = []
    th.register_pre_step_gen_callback(
        lambda flush_time: seen.append(flush_time)
    )
    th._advance_flush_time(9.0)
    assert seen == [9.0]


def test_a_callback_added_during_the_flush_is_not_run():
    th = _make_toolhead()
    order = []

    def first_cb(flush_time):
        order.append("first")
        th.register_pre_step_gen_callback(lambda ft: order.append("second"))

    th.register_pre_step_gen_callback(first_cb)
    th._advance_flush_time(9.0)
    # The list is copied before it is walked
    assert order == ["first"]
