"""Provide explicit capability declarations for isolated scientific-planner tests."""

import pytest

from psi4_parser.formal import (
    BasisCapability,
    BasisFunctions,
    CapabilityCatalog,
    Evidence,
    MethodCapability,
    OptionCapability,
    QuantityType,
)
from psi4_parser.formal.science import Driver


@pytest.fixture(name="formal_profile")
def formal_profile_fixture() -> CapabilityCatalog:
    """Return synthetic capability declarations for isolated planner tests."""
    drivers: tuple[Driver, ...] = (
        "energy",
        "optimize",
        "frequency",
        "gradient",
        "hessian",
        "properties",
    )
    methods = tuple(
        MethodCapability(
            method="scf",
            driver=driver,
            reference="rhf",
            status="supported",
            quantity=(
                QuantityType(
                    meaning="gradient", unit="hartree/bohr", shape=("atoms", 3)
                )
                if driver == "gradient"
                else QuantityType(
                    meaning="hessian",
                    unit="hartree/bohr^2",
                    shape=("3*atoms", "3*atoms"),
                )
                if driver == "hessian"
                else QuantityType(meaning="electronic_energy", unit="hartree")
            ),
            features=("ghost_centers", "constraints", "frozen_core"),
            options=("scf_type",),
            evidence=("fixture",),
        )
        for driver in drivers
    )
    return CapabilityCatalog(
        id="synthetic-planner-fixture",
        evidence=(
            Evidence(
                id="fixture",
                source="Planner tests: explicit synthetic declarations",
                kind="declaration",
                application_version="fixture/1",
            ),
        ),
        methods=methods,
        bases=(
            BasisCapability(
                name="sto-3g",
                status="supported",
                elements=("H",),
                functions=(BasisFunctions(element="H", spherical=1, cartesian=1),),
                evidence=("fixture",),
            ),
        ),
        options=(
            OptionCapability(
                name="scf_type",
                status="supported",
                values=("pk", "df"),
                evidence=("fixture",),
            ),
        ),
    )
