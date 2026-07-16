# Definitions of the supported input shapers
#
# Copyright (C) 2020-2021  Dmitry Butyugin <dmbutyugin@google.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import collections
import math
import mathutil
import re

SHAPER_VIBRATION_REDUCTION = 20.0
DEFAULT_DAMPING_RATIO = 0.1

InputShaperCfg = collections.namedtuple(
    "InputShaperCfg", ("name", "init_func", "min_freq", "max_damping_ratio")
)


class ShaperError(Exception):
    pass


def get_none_shaper():
    return ([], [])


def get_zv_shaper(shaper_freq, damping_ratio):
    df = math.sqrt(1.0 - damping_ratio**2)
    K = math.exp(-damping_ratio * math.pi / df)
    t_d = 1.0 / (shaper_freq * df)
    A = [1.0, K]
    T = [0.0, 0.5 * t_d]
    return (A, T)


def get_zvd_shaper(shaper_freq, damping_ratio):
    df = math.sqrt(1.0 - damping_ratio**2)
    K = math.exp(-damping_ratio * math.pi / df)
    t_d = 1.0 / (shaper_freq * df)
    A = [1.0, 2.0 * K, K**2]
    T = [0.0, 0.5 * t_d, t_d]
    return (A, T)


def get_mzv_coeffs(n, t):
    if n < 3:
        raise ShaperError("Too small n=%d, must be at least 3" % n)
    if n <= 2 * t + 1 + 1e-7:
        raise ShaperError(
            "Too large t=%.6f for n=%d, must be less than %.6f"
            % (t, n, 0.5 * (n - 1))
        )
    # Projected shaper duration with n -> \infinity for computing shaper zeros
    tau = t * (n - 2.0) / (n - 2.0 * t - 1.0)
    T = [i * t / (n - 1.0) for i in range(n)]
    # Build a system of equations for A. The first equation is sum(A) = 1
    M = [[1.0] * n]
    F = [1.0]
    # Ensure correct placement of shaper zeros.
    for i in range(n - 1):
        W = [2.0 * math.pi * (1.0 + i / tau) * tj for tj in T]
        M.append([math.cos(w) for w in W])
        M.append([math.sin(w) for w in W])
        F.append(0.0)
        F.append(0.0)
    M_inv = mathutil.pseudo_inverse(M)
    if M_inv is None:
        raise ShaperError("Ill-formed shaper with n=%d, t=%.6f" % (n, t))
    A = mathutil.mat_mat_mul([F], mathutil.mat_transp(M_inv))[0]
    if any(a < -0.00001 for a in A):
        raise ShaperError("Negative-valued shaper with n=%d, t=%.6f" % (n, t))
    return (A, T)


def get_mzv_shaper(shaper_freq, damping_ratio, n=3, t=0.0, tau=0.0):
    if not tau and not t:
        t = 0.75
    elif tau:
        # Infer total shaper duration from a projected shaper duration with
        # n -> \infinity
        t = tau * (n - 1.0) / (n + 2.0 * tau - 2.0)
    A, T = get_mzv_coeffs(n, t)
    # Apply damping
    df = math.sqrt(1.0 - damping_ratio**2)
    K = math.exp(-2.0 * t * damping_ratio * math.pi / ((n - 1.0) * df))
    t_d = 1.0 / (shaper_freq * df)
    Kp = K
    for i in range(1, n):
        T[i] *= t_d
        A[i] *= Kp
        Kp *= K
    return (A, T)


def get_ei_shaper(shaper_freq, damping_ratio,
                   v_tol=1.0 / SHAPER_VIBRATION_REDUCTION):
    df = math.sqrt(1.0 - damping_ratio**2)
    K = math.exp(-damping_ratio * math.pi / df)
    t_d = 1.0 / (shaper_freq * df)

    a1 = 0.25 * (1.0 + v_tol)
    a2 = 0.5 * (1.0 - v_tol) * K
    a3 = a1 * K * K

    A = [a1, a2, a3]
    T = [0.0, 0.5 * t_d, t_d]
    return (A, T)


def _get_shaper_from_expansion_coeffs(shaper_freq, damping_ratio, t, a):
    tau = 1.0 / shaper_freq
    T = []
    A = []
    n = len(a)
    k = len(a[0])
    for i in range(n):
        u = t[i][k - 1]
        v = a[i][k - 1]
        for j in range(k - 1):
            u = u * damping_ratio + t[i][k - j - 2]
            v = v * damping_ratio + a[i][k - j - 2]
        T.append(u * tau)
        A.append(v)
    return (A, T)


def get_2hump_ei_shaper(shaper_freq, damping_ratio):
    v_tol = 1.0 / SHAPER_VIBRATION_REDUCTION  # vibration tolerance
    V2 = v_tol**2
    df = math.sqrt(1.0 - damping_ratio**2)
    K = math.exp(-damping_ratio * math.pi / df)
    t_d = 1.0 / (shaper_freq * df)

    X = pow(V2 * (math.sqrt(1.0 - V2) + 1.0), 1.0 / 3.0)
    a1 = (3.0 * X * X + 2.0 * X + 3.0 * V2) / (16.0 * X)
    a2 = (0.5 - a1) * K
    a3 = a2 * K
    a4 = a1 * K * K * K

    A = [a1, a2, a3, a4]
    T = [0.0, 0.5 * t_d, t_d, 1.5 * t_d]
    return (A, T)


def get_3hump_ei_shaper(shaper_freq, damping_ratio):
    v_tol = 1.0 / SHAPER_VIBRATION_REDUCTION  # vibration tolerance
    df = math.sqrt(1.0 - damping_ratio**2)
    K = math.exp(-damping_ratio * math.pi / df)
    t_d = 1.0 / (shaper_freq * df)

    K2 = K * K
    a1 = 0.0625 * (
        1.0
        + 3.0 * v_tol
        + 2.0 * math.sqrt(2.0 * (v_tol + 1.0) * v_tol)
    )
    a2 = 0.25 * (1.0 - v_tol) * K
    a3 = (0.5 * (1.0 + v_tol) - 2.0 * a1) * K2
    a4 = a2 * K2
    a5 = a1 * K2 * K2

    A = [a1, a2, a3, a4, a5]
    T = [0.0, 0.5 * t_d, t_d, 1.5 * t_d, 2.0 * t_d]
    return (A, T)


# min_freq for each shaper is chosen to have projected max_accel ~= 1500
INPUT_SHAPERS = [
    InputShaperCfg(
        name="zv", init_func=get_zv_shaper, min_freq=21.0,
        max_damping_ratio=0.99
    ),
    InputShaperCfg(
        name="mzv", init_func=get_mzv_shaper, min_freq=23.0,
        max_damping_ratio=0.99
    ),
    InputShaperCfg(
        name="zvd", init_func=get_zvd_shaper, min_freq=29.0,
        max_damping_ratio=0.99
    ),
    InputShaperCfg(
        name="ei", init_func=get_ei_shaper, min_freq=29.0,
        max_damping_ratio=0.4
    ),
    InputShaperCfg(
        name="2hump_ei", init_func=get_2hump_ei_shaper, min_freq=39.0,
        max_damping_ratio=0.3
    ),
    InputShaperCfg(
        name="3hump_ei", init_func=get_3hump_ei_shaper, min_freq=48.0,
        max_damping_ratio=0.2
    ),
]


def get_shaper_cfg(shaper_name):
    m = re.match(r"(\w+)\s*\((.*)\)$", shaper_name)
    if m:
        shaper_name = m.group(1)
    for s in INPUT_SHAPERS:
        if shaper_name == s.name:
            return s
    return None


def init_shaper(shaper_name, shaper_freq, damping_ratio, error=None):
    try:
        m = re.match(r"(\w+)\s*\((.*)\)$", shaper_name)
        args_l = []
        args_kv = {}
        if m:
            shaper_name = m.group(1)
            args = m.group(2)
            if args:
                parsed_args = re.findall(
                    r"(?:(\w+)\s*=\s*)?\s*([\d.]+)", args
                )

                def parse_val(s):
                    if "." in s:
                        return float(s)
                    return int(s)

                args_l = [parse_val(v) for k, v in parsed_args if not k]
                args_kv = {k: parse_val(v) for k, v in parsed_args if k}
                if args_l and args_kv:
                    raise ShaperError(
                        "Mixing named and non-named shaper"
                        " parameters is not supported"
                    )
        for s in INPUT_SHAPERS:
            if shaper_name == s.name:
                return s.init_func(shaper_freq, damping_ratio,
                                   *args_l, **args_kv)
    except ShaperError as e:
        if error is None:
            raise
        raise error("Failed to initialize shaper: %s" % str(e))
    return None
