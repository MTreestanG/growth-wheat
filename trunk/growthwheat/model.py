# -*- coding: latin-1 -*-

from __future__ import division  # use "//" to do integer division
import parameters

"""
    growthwheat.model
    ~~~~~~~~~~~~~

    The module :mod:`growthwheat.model` defines the equations of the kinetic of leaf growth (mass flows) according to leaf elongation. Also includes root growth.

    :copyright: Copyright 2014-2015 INRA-ECOSYS, see AUTHORS.
    :license: TODO, see LICENSE for details.

    .. seealso:: Barillot et al. 2015.
"""

"""
    Information about this versioned file:
        $LastChangedBy$
        $LastChangedDate$
        $LastChangedRevision$
        $URL$
        $Id$
"""


def calculate_delta_leaf_enclosed_mstruct(leaf_L, delta_leaf_L):
    """ Relation between length and mstruct for the leaf segment located in the hidden zone during the exponential-like growth phase.
    Parameters alpha_mass_growth and beta_mass_growth estimated from Williams (1975) and expressed in g of dry mass. #TODO : Check the ref (Williams 1960?)
    Parameter RATIO_MSTRUCT_DM is then used to convert in g of structural dry mass.

    :Parameters:
        - `leaf_L` (:class:`float`) - Total leaf length (m)
        - `delta_leaf_L` (:class:`float`) - delta of leaf length (m)
    :Returns:
        delta_leaf_enclosed_mstruct (g)
    :Returns Type:
        :class:`float`
    """
    return parameters.ALPHA * parameters.BETA * leaf_L**(parameters.BETA-1) * delta_leaf_L * parameters.RATIO_MSTRUCT_DM

def calculate_delta_leaf_enclosed_mstruct_postE(leaf_pseudo_age, leaf_pseudostem_L, LSSW, mstruct):
    """ mstruct of the enclosed leaf from the emergence of the previous leaf to the end of elongation (automate function depending on leaf pseudo age and final mstruct).
    Final mstruct of the enclosed leaf matches sheath mstruct calculation when it is mature.
    #TODO : Hiddenzone mstruct calculation will not work for sheath sorten than previous one.

    :Parameters:
        - `leaf_pseudo_age` (:class:`float`) - Pseudo age of the leaf since beginning of automate elongation (s)
        - 'leaf_pseudostem_L' (:class:`float`) Pseudostem length (m)
        - `LSSW` (:class:`float`) - Lineic Structural Sheath Weight (g m-1).
        - `mstruct` (:class:`float`) - current mstruct of the enclosed part of the leaf (g)
    :Returns:
        delta_leaf_enclosed_mstruct (g)
    :Returns Type:
        :class:`float`
    """

    enclosed_mstruct_max = leaf_pseudostem_L * LSSW
    if leaf_pseudo_age <= parameters.tb:
        enclosed_mstruct = parameters.FITTED_L0 * enclosed_mstruct_max
    elif leaf_pseudo_age < parameters.te:
        enclosed_mstruct = min(enclosed_mstruct_max, enclosed_mstruct_max * (abs((1 + (max(0, (parameters.te - leaf_pseudo_age)) / (parameters.te - parameters.tm)))
                                                 * (min(1.0, float(leaf_pseudo_age - parameters.tb) / float(parameters.te - parameters.tb)) **
                                                    ((parameters.te - parameters.tb) / (parameters.te - parameters.tm)))) + parameters.OFFSET_LEAF))
    else:
        enclosed_mstruct = enclosed_mstruct_max

    return enclosed_mstruct - mstruct

def calculate_delta_internode_enclosed_mstruct(internode_L, delta_internode_L):
    """ Relation between length and mstruct for the internode segment located in the hidden zone.
    Same relationship than for enclosed leaf corrected by RATIO_ENCLOSED_LEAF_INTERNODE.
    Parameters alpha_mass_growth and beta_mass_growth estimated from Williams (1975) and expressed in g of dry mass.
    Parameter RATIO_MSTRUCT_DM is then used to convert in g of structural dry mass.

    :Parameters:
        - `internode_L` (:class:`float`) - Enclosed internode length (m)
        - `delta_internode_L` (:class:`float`) - delta of enclosed internode length (m)
    :Returns:
        delta_enclosed_internode_mstruct (g)
    :Returns Type:
        :class:`float`
    """
    # TODO: internode mstruct should increase to meet internode_L * LINW at the end of its elongation(like leaf). However, since an internode might never emerge, its mstruct should increase from the end of its exponential-like phase.

    return parameters.RATIO_ENCLOSED_LEAF_INTERNODE * parameters.ALPHA * parameters.BETA * internode_L**(parameters.BETA-1) * delta_internode_L * parameters.RATIO_MSTRUCT_DM

def calculate_delta_internode_enclosed_mstruct_postL(internode_pseudo_age, internode_pseudostem_L,LSIW, mstruct ):
    """ mstruct of the enclosed internode from the ligulation of the previous leaf to the end of elongation (automate function depending on internode pseudo age and final mstruct).
    Final mstruct of the enclosed internode matches internode mstruct calculation when it is mature.

    :Parameters:
        - `internode_pseudo_age` (:class:`float`) - Pseudo age of the internode since beginning of automate elongation (s)
        - 'internode_pseudostem_L' (:class:`float`) Pseudostem length of the internode (m)
        - `LSIW` (:class:`float`) - Lineic Structural Internode Weight (g m-1).
        - `mstruct` (:class:`float`) - current mstruct of the enclosed part of the internode (g)
    :Returns:
        delta_internode_enclosed_mstruct (g)
    :Returns Type:
        :class:`float`
    """
    enclosed_mstruct_max = internode_pseudostem_L * LSIW
    if internode_pseudo_age <= parameters.tb_IN:
        enclosed_mstruct = (1 / parameters.SCALING_FACTOR_INT) * enclosed_mstruct_max
    elif internode_pseudo_age < parameters.te_IN:
        enclosed_mstruct = min(enclosed_mstruct_max, enclosed_mstruct_max * (abs((1 + (max(0, (parameters.te_IN - internode_pseudo_age)) / (parameters.te_IN - parameters.tm_IN))) *
                                                                (min(1.0, float(internode_pseudo_age - parameters.tb_IN) /
                                                                     float(parameters.te_IN - parameters.tb_IN)) ** ((parameters.te_IN - parameters.tb_IN) /
                                                                                                                     (parameters.te_IN - parameters.tm_IN)))) + parameters.OFFSET_INT))
    else:
        enclosed_mstruct = enclosed_mstruct_max
    return enclosed_mstruct - mstruct

def calculate_delta_emerged_tissue_mstruct(SW, previous_mstruct, metric):
    """ delta mstruct of emerged tissue (lamina, sheath and internode). Calculated from tissue area.

    :Parameters:
        - `SW` (:class:`float`) - For Lamina : Structural Specific Weight (g m-2); For sheath and internode : Lineic Structural Weight (g m-1)
        - `previous_mstruct` (:class:`float`) - mstruct at the previous time step i.e. not yet updated (g)
        - `metric` (:class:`float`) - For Lamina : Area at the current time step, as updated by the geometrical model (m2); For sheath and internode : Length at the current time step (m)
    :Returns:
        delta mstruct (g)
    :Returns Type:
        :class:`float`
    """
    updated_mstruct = SW * metric
    delta_mstruct = updated_mstruct - previous_mstruct
    return delta_mstruct


def calculate_delta_Nstruct(delta_mstruct):
    """ delta Nstruct of hidden zone and emerged tissue (lamina and sheath).

    :Parameters:
        - `delta_mstruct` (:class:`float`) - delta of mstruct (g)
    :Returns:
        delta Nstruct (g)
    :Returns Type:
        :class:`float`
    """
    return delta_mstruct * parameters.RATIO_AMINO_ACIDS_MSTRUCT


def calculate_export(delta_mstruct, metabolite, hiddenzone_mstruct):
    """Export of metabolite from the hidden zone towards the emerged part of the leaf integrated over delta_t.

    :Parameters:
        - `delta_mstruct` (:class:`float`) - Delta of structural dry mass of the emerged part of the leaf (g)
        - `metabolite` (:class:`float`) - Metabolite amount in the hidden zone (�mol C or N)
        - `hiddenzone_mstruct` (:class:`float`) - Structural mass of the hidden zone (g)

    :Returns:
        metabolite export (�mol N)
    :Returns Type:
        :class:`float`
    """
    return delta_mstruct * max(0, (metabolite / hiddenzone_mstruct))


def calculate_s_Nstruct_amino_acids(delta_hiddenzone_Nstruct, delta_lamina_Nstruct, delta_sheath_Nstruct):
    """Consumption of amino acids for the calculated mstruct growth (�mol N consumed by mstruct growth)

    :Parameters:
        - `delta_hiddenzone_Nstruct` (:class:`float`) - Nstruct growth of the hidden zone (g)
        - `delta_lamina_Nstruct` (:class:`float`) - Nstruct growth of the lamina (g)
        - `delta_sheath_Nstruct` (:class:`float`) - Nstruct growth of the sheath (g)
    :Returns:
        Amino acid consumption (�mol N)
    :Returns Type:
        :class:`float`
    """
    return (delta_hiddenzone_Nstruct + delta_lamina_Nstruct + delta_sheath_Nstruct) / parameters.N_MOLAR_MASS * 1E6


def calculate_s_mstruct_sucrose(delta_hiddenzone_mstruct, delta_lamina_mstruct, delta_sheath_mstruct, s_Nstruct_amino_acids_N):
    """Consumption of sucrose for the calculated mstruct growth (�mol C consumed by mstruct growth)

    :Parameters:
        - `delta_hiddenzone_mstruct` (:class:`float`) - mstruct growth of the hidden zone (g)
        - `delta_lamina_mstruct` (:class:`float`) - mstruct growth of the lamina (g)
        - `delta_sheath_mstruct` (:class:`float`) - mstruct growth of the sheath (g)
        - `s_Nstruct_amino_acids_N` (:class:`float`) - Total amino acid consumption (�mol N) due to Nstruct (�mol N)
    :Returns:
        Sucrose consumption (�mol C)
    :Returns Type:
        :class:`float`
    """
    s_Nstruct_amino_acids = s_Nstruct_amino_acids_N / parameters.AMINO_ACIDS_N_RATIO   #: �mol of AA
    s_mstruct_amino_acids_C = s_Nstruct_amino_acids * parameters.AMINO_ACIDS_C_RATIO   #: �mol of C coming from AA
    s_mstruct_C = (delta_hiddenzone_mstruct + delta_lamina_mstruct + delta_sheath_mstruct) * parameters.RATIO_SUCROSE_MSTRUCT / parameters.C_MOLAR_MASS * 1E-6  #: Total C used for mstruct growth (�mol C)
    s_mstruct_sucrose_C = s_mstruct_C - s_mstruct_amino_acids_C                        #: �mol of coming from sucrose

    return s_mstruct_sucrose_C


# Roots
def calculate_roots_mstruct_growth(sucrose, amino_acids, mstruct, delta_t):
    """Root structural dry mass growth integrated over delta_t

    : Parameters:
        - `sucrose` (:class:`float`) - Amount of sucrose in roots (�mol C)
        - `amino_acids` (:class:`float`) - Amount of amino acids in roots (�mol N)
        - `mstruct` (:class:`float`) - Root structural mass (g)

    : Returns:
        mstruct_C_growth (�mol C), mstruct_growth (g), Nstruct_growth (g), Nstruct_N_growth (�mol N)

    :Returns Type:
        :class:`float`
    """
    conc_sucrose = max(0, sucrose/mstruct)

    mstruct_C_growth = (conc_sucrose * parameters.VMAX_ROOTS_GROWTH) / (conc_sucrose + parameters.K_ROOTS_GROWTH) * delta_t * mstruct     #: root growth in C (�mol of C)
    mstruct_growth = (mstruct_C_growth*1E-6 * parameters.C_MOLAR_MASS) / parameters.RATIO_C_MSTRUCT_ROOTS                                 #: root growth (g of structural dry mass)
    Nstruct_growth = mstruct_growth * parameters.RATIO_N_MSTRUCT_ROOTS_                                                                   #: root growth in N (g of structural dry mass)
    Nstruct_N_growth = min(amino_acids, (Nstruct_growth / parameters.N_MOLAR_MASS)*1E6)                                                   #: root growth in nitrogen (�mol N)

    return mstruct_C_growth, mstruct_growth, Nstruct_growth, Nstruct_N_growth
