# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- http://mdanalysis.googlecode.com
# Copyright (c) 2006-2011 Naveen Michaud-Agrawal,
#               Elizabeth J. Denning, Oliver Beckstein,
#               and contributors (see website for details)
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
#     N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and
#     O. Beckstein. MDAnalysis: A Toolkit for the Analysis of
#     Molecular Dynamics Simulations. J. Comput. Chem. 32 (2011), 2319--2327,
#     doi:10.1002/jcc.21787
#

import MDAnalysis
import MDAnalysis as mda
import MDAnalysis.coordinates
import MDAnalysis.coordinates.core

import numpy as np
from numpy.testing import *
from nose.plugins.attrib import attr

from MDAnalysis.tests.datafiles import PSF,DCD,DCD_empty,PDB_small,PDB,CRD,XTC,TRR,GRO, \
    XYZ,XYZ_bz2,XYZ_psf, PRM,TRJ,TRJ_bz2, PRMpbc, TRJpbc_bz2, PQR

import os
import tempfile
import itertools

def atom_distance(a, b):
    """Calculate the distance between two atoms a and b."""
    r = a.pos - b.pos
    return np.sqrt(np.sum(r**2))

class RefAdKSmall(object):
    """Mixin class to provide comparison numbers.

    Based on small PDB with AdK (:data:`PDB_small`).

    .. Note:: All distances must be in ANGSTROEM as this is the
       MDAnalysis default unit. All readers must return Angstroem by
       default.
    """
    ref_coordinates = {
        'A10CA': np.array([ -1.198, 7.937, 22.654]),   # G11:CA, copied frm adk_open.pdb
        }
    ref_distances = {'endtoend': 11.016959}
    ref_E151HA2_index = 2314
    ref_numatoms = 3341
    ref_charmm_totalcharge = -4.0
    ref_charmm_Hcharges = [0.33] + 203*[0.31]
    ref_charmm_ArgCAcharges = 13 * [0.07]
    ref_charmm_ProNcharges = 10 * [-0.29]
    ref_unitcell = np.array([0,0,0, 0,0,0], dtype=np.float32)
    ref_volume = 0.0

class RefAdK(object):
    """Mixin class to provide comparison numbers.

    Based on PDB/GRO with AdK in water + Na+ (:data:`PDB`).

    .. Note:: All distances must be in ANGSTROEM as this is the
       MDAnalysis default unit. All readers must return Angstroem by
       default.
    """
    ref_coordinates = {
        'A10CA': np.array([ 62.97600174,  62.08800125,  20.2329998 ]),  # Angstroem as MDAnalysis unit!!
        }
    ref_distances = {'endtoend': 9.3513174}
    ref_E151HA2_index = 2314
    ref_numatoms = 47681
    ref_Na_sel_size = 4
    # CRYST1 80.017   80.017   80.017  60.00  60.00  90.00
    ref_unitcell = np.array([ 80.017,  80.017,  80.017,  60., 60., 90.], dtype=np.float32)
    ref_volume = 362270.0  # computed with Gromacs

class Ref2r9r(object):
    """Mixin class to provide comparison numbers.

    Based on S6 helices of chimeric Kv channel

    .. Note:: All distances must be in ANGSTROEM as this is the
       MDAnalysis default unit. All readers must return Angstroem by
       default.
    """
    ref_numatoms = 1284
    ref_sum_centre_of_geometry = -98.24146
    ref_numframes = 10

class TestXYZReader(TestCase, Ref2r9r):
    def setUp(self):
        self.universe = mda.Universe(XYZ_psf, XYZ)
        self.prec = 3 # 4 decimals in xyz file

    def tearDown(self):
        del self.universe

    def test_load_xyz(self):
        U = self.universe
        assert_equal(len(U.atoms), self.ref_numatoms, "load Universe from PSF and XYZ")

    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, self.ref_numatoms, "wrong number of atoms")

    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, self.ref_numframes, "wrong number of frames in xyz")

    def test_sum_centres_of_geometry(self):
        centreOfGeometry=0

        for i in self.universe.trajectory:
            sel = self.universe.selectAtoms("all")
            centreOfGeometry+=sum(sel.centerOfGeometry())

        assert_almost_equal(centreOfGeometry, self.ref_sum_centre_of_geometry, self.prec,
                            err_msg="sum of centers of geometry over the trajectory do not match")


class TestCompressedXYZReader(TestCase, Ref2r9r):
    def setUp(self):
        self.universe = mda.Universe(XYZ_psf, XYZ_bz2)
        self.prec = 3 # 4 decimals in xyz file

    def tearDown(self):
        del self.universe

    def test_load_xyz(self):
        U = self.universe
        assert_equal(len(U.atoms), self.ref_numatoms, "load Universe from PSF and XYZ")

    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, self.ref_numatoms, "wrong number of atoms")

    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, self.ref_numframes, "wrong number of frames in xyz")

    def test_sum_centres_of_geometry(self):
        centreOfGeometry=0

        for i in self.universe.trajectory:
            sel = self.universe.selectAtoms("all")
            centreOfGeometry+=sum(sel.centerOfGeometry())

        assert_almost_equal(centreOfGeometry, self.ref_sum_centre_of_geometry, self.prec,
                            err_msg="sum of centers of geometry over the trajectory do not match")


class RefACHE(object):
    """Mixin class to provide comparison numbers.

    ACHE peptide

    # COM check in VMD::

        set p [atomselect top "not water"]
        set total {0 0 0};
        for {set i 0} {$i < 11} {incr i} {
           $p frame $i; set total [vecadd $total [measure center $p]]}

        puts [vecsum $total]
        # 472.2592159509659

    """
    ref_numatoms = 252
    ref_proteinatoms = ref_numatoms
    ref_sum_centre_of_geometry = 472.2592159509659 #430.44807815551758
    ref_numframes = 11
    ref_periodic = False

class RefCappedAla(object):
    """Mixin class to provide comparison numbers.

    Capped Ala in water

    # COM check in VMD (load trajectory as *AMBER with periodic box*!)::

        set p [atomselect top "not water"]
        set total {0 0 0};
        for {set i 0} {$i < 11} {incr i} {
           $p frame $i; set total [vecadd $total [measure center $p]]}

        puts [vecsum $total]
        # 686.276834487915

    """
    ref_numatoms = 5071
    ref_proteinatoms = 22
    ref_sum_centre_of_geometry =  686.276834487915
    ref_numframes = 11
    ref_periodic = True


class _TRJReaderTest(TestCase):
    # use as a base class (override setUp()) and mixin a reference
    def tearDown(self):
        del self.universe

    def test_load_prm(self):
        U = self.universe
        assert_equal(len(U.atoms), self.ref_numatoms, "load Universe from PRM and TRJ")

    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, self.ref_numatoms, "wrong number of atoms")

    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, self.ref_numframes, "wrong number of frames in xyz")

    def test_periodic(self):
        assert_equal(self.universe.trajectory.periodic, self.ref_periodic)

    def test_amber_proteinselection(self):
        protein = self.universe.selectAtoms('protein')
        assert_equal(protein.numberOfAtoms(), self.ref_proteinatoms, "error in protein selection (HIS or termini?)")

    def test_sum_centres_of_geometry(self):
        protein = self.universe.selectAtoms('protein')
        total = np.sum([protein.centerOfGeometry() for ts in self.universe.trajectory])
        assert_almost_equal(total, self.ref_sum_centre_of_geometry, self.prec,
                            err_msg="sum of centers of geometry over the trajectory do not match")


class TestTRJReader(_TRJReaderTest, RefACHE):
    def setUp(self):
        self.universe = mda.Universe(PRM, TRJ)
        self.prec = 3

class TestBzippedTRJReader(TestTRJReader):
    def setUp(self):
        self.universe = mda.Universe(PRM, TRJ_bz2)
        self.prec = 3

class TestBzippedTRJReaderPBC(_TRJReaderTest, RefCappedAla):
    def setUp(self):
        self.universe = mda.Universe(PRMpbc, TRJpbc_bz2)
        self.prec = 3

class _SingleFrameReader(TestCase, RefAdKSmall):
    # see TestPDBReader how to set up!

    def tearDown(self):
        del self.universe

    def test_flag_permissive_pdb_reader(self):
        """test_flag_permissive_pdb_reader: permissive_pdb_reader==True enables primitive PDB reader"""
        assert_equal(mda.core.flags['permissive_pdb_reader'], True,
                     "'permissive_pdb_reader' flag should be True as MDAnalysis default")

    def test_load_file(self):
        U = self.universe
        assert_equal(len(U.atoms), self.ref_numatoms, "load Universe from file %s" % U.trajectory.filename)
        assert_equal(U.atoms.selectAtoms('resid 150 and name HA2').atoms[0],
                     U.atoms[self.ref_E151HA2_index], "Atom selections")

    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, self.ref_numatoms, "wrong number of atoms")

    def test_numres(self):
        assert_equal(self.universe.atoms.numberOfResidues(), 214, "wrong number of residues")

    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, 1, "wrong number of frames in pdb")

    def test_time(self):
        assert_equal(self.universe.trajectory.time, 0.0, "wrong time of the frame")

    def test_frame(self):
        assert_equal(self.universe.trajectory.frame, 0, "wrong frame number")

    def test_dt(self):
        """testing that accessing universe.trajectory.dt raises a KeyError for single frame readers"""
        assert_raises(KeyError, self.universe.trajectory.__getattribute__, "dt")

    def test_coordinates(self):
        A10CA = self.universe.atoms.CA[10]
        # restrict accuracy to maximum in PDB files (3 decimals)
        assert_almost_equal(A10CA.pos, self.ref_coordinates['A10CA'], 3,
                            err_msg="wrong coordinates for A10:CA")

    def test_distances(self):
        NTERM = self.universe.atoms.N[0]
        CTERM = self.universe.atoms.C[-1]
        d = atom_distance(NTERM, CTERM)
        assert_almost_equal(d, self.ref_distances['endtoend'], self.prec,
                            err_msg="distance between M1:N and G214:C")

class TestPDBReader(_SingleFrameReader):
    def setUp(self):
        ##mda.core.flags['permissive_pdb_reader'] = False # enable Bio.PDB reader!!
        # use permissive=False instead of changing the global flag as this
        # can lead to race conditions when testing in parallel
        self.universe = mda.Universe(PDB_small, permissive=False)
        self.prec = 3  # 3 decimals in PDB spec http://www.wwpdb.org/documentation/format32/sect9.html#ATOM

class TestPSF_CRDReader(_SingleFrameReader):
    def setUp(self):
        self.universe = mda.Universe(PSF, CRD)
        self.prec = 5  # precision in CRD (at least we are writing %9.5f)

class TestPSF_PDBReader(TestPDBReader):
    def setUp(self):
        # mda.core.flags['permissive_pdb_reader'] = False
        self.universe = mda.Universe(PSF, PDB_small, permissive=False)
        self.prec = 3  # 3 decimals in PDB spec http://www.wwpdb.org/documentation/format32/sect9.html#ATOM

class TestPrimitivePDBReader(_SingleFrameReader):
    def setUp(self):
        self.universe = mda.Universe(PDB_small, permissive=True)
        self.prec = 3  # 3 decimals in PDB spec http://www.wwpdb.org/documentation/format32/sect9.html#ATOM

class TestPSF_PrimitivePDBReader(TestPrimitivePDBReader):
    def setUp(self):
        self.universe = mda.Universe(PSF, PDB_small, permissive=True)
        self.prec = 3  # 3 decimals in PDB spec http://www.wwpdb.org/documentation/format32/sect9.html#ATOM

class TestPrimitivePDBWriter(TestCase):
    def setUp(self):
        self.universe = mda.Universe(PSF, PDB_small, permissive=True)
        self.prec = 3  # 3 decimals in PDB spec http://www.wwpdb.org/documentation/format32/sect9.html#ATOM
        ext = ".pdb"
        fd, self.outfile = tempfile.mkstemp(suffix=ext)
        fd, self.outfile2 = tempfile.mkstemp(suffix=ext)

    def tearDown(self):
        try:
            os.unlink(self.outfile)
        except OSError:
            pass
        try:
            os.unlink(self.outfile2)
        except OSError:
            pass
        del self.universe

    def test_writer(self):
        self.universe.atoms.write(self.outfile)
        u = mda.Universe(PSF, self.outfile, permissive=True)
        assert_almost_equal(u.atoms.coordinates(), self.universe.atoms.coordinates(), self.prec,
                            err_msg="Writing PDB file with PrimitivePDBWriter does not reproduce original coordinates")

    @attr('issue')
    def test_check_coordinate_limits_min(self):
        """Test that illegal PDB coordinates (x <= -999.9995 A) are caught with ValueError (Issue 57)"""
        # modify coordinates so we need our own copy or we could mess up parallel tests
        u = mda.Universe(PSF, PDB_small, permissive=True)
        u.atoms[2000].pos[1] = -999.9995
        assert_raises(ValueError, u.atoms.write, self.outfile2)
        del u

    @attr('issue')
    def test_check_coordinate_limits_max(self):
        """Test that illegal PDB coordinates (x > 9999.9995 A) are caught with ValueError (Issue 57)"""
        # modify coordinates so we need our own copy or we could mess up parallel tests
        u = mda.Universe(PSF, PDB_small, permissive=True)
        u.atoms[1000].pos[1] =  9999.9996   # OB: 9999.99951 is not caught by '<=' ?!?
        assert_raises(ValueError, u.atoms.write, self.outfile2)
        del u

class TestPQRReader(_SingleFrameReader):
    def setUp(self):
        self.universe = mda.Universe(PQR)
        self.prec = 3  # 3 decimals in PDB spec http://www.wwpdb.org/documentation/format32/sect9.html#ATOM

    def test_totalCharge(self):
        assert_almost_equal(self.universe.atoms.totalCharge(), self.ref_charmm_totalcharge, 3,
                            "Total charge (in CHARMM) does not match expected value.")

    def test_hydrogenCharges(self):
        assert_almost_equal(self.universe.atoms.H.charges(), self.ref_charmm_Hcharges, 3,
                            "Charges for H atoms do not match.")

    # Note that the whole system gets the sysID 'SYSTEM' for the PQR file (when read with
    # a PSF it is 's4AKE')
    def test_ArgCACharges(self):
        assert_almost_equal(self.universe.SYSTEM.ARG.CA.charges(), self.ref_charmm_ArgCAcharges, 3,
                            "Charges for CA atoms in Arg residues do not match.")

    def test_ProNCharges(self):
        assert_almost_equal(self.universe.SYSTEM.PRO.N.charges(), self.ref_charmm_ProNcharges, 3,
                            "Charges for N atoms in Pro residues do not match.")


class TestGROReader(TestCase, RefAdK):
    def setUp(self):
        self.universe = mda.Universe(GRO)
        self.ts = self.universe.trajectory.ts
        self.prec = 2  # lower prec in gro!! (3 decimals nm -> 2 decimals in Angstroem)

    def tearDown(self):
        del self.universe
        del self.ts

    def test_flag_convert_gromacs_lengths(self):
        assert_equal(mda.core.flags['convert_gromacs_lengths'], True,
                     "MDAnalysis.core.flags['convert_gromacs_lengths'] should be True by default")

    def test_load_gro(self):
        U = self.universe
        assert_equal(len(U.atoms), self.ref_numatoms, "load Universe from small GRO")
        assert_equal(U.atoms.selectAtoms('resid 150 and name HA2').atoms[0],
                     U.atoms[self.ref_E151HA2_index], "Atom selections")

    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, self.ref_numatoms, "wrong number of atoms")

    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, 1, "wrong number of frames")

    def test_time(self):
        assert_equal(self.universe.trajectory.time, 0.0, "wrong time of the frame")

    def test_frame(self):
        assert_equal(self.universe.trajectory.frame, 0, "wrong frame number")

    def test_dt(self):
        """testing that accessing universe.trajectory.dt raises a KeyError for single frame readers"""
        assert_raises(KeyError, self.universe.trajectory.__getattribute__, "dt")

    def test_coordinates(self):
        A10CA = self.universe.SYSTEM.CA[10]
        assert_almost_equal(A10CA.pos, self.ref_coordinates['A10CA'], self.prec,
                            err_msg="wrong coordinates for A10:CA")

    def test_distances(self):
        # NOTE that the prec is only 1 decimal: subtracting two low precision coordinates
        #      low prec: 9.3455122920041109; high prec (from pdb): 9.3513174
        NTERM = self.universe.SYSTEM.N[0]
        CTERM = self.universe.SYSTEM.C[-1]
        d = atom_distance(NTERM, CTERM)
        assert_almost_equal(d, self.ref_distances['endtoend'], self.prec - 1,  # note low prec!!
                            err_msg="distance between M1:N and G214:C")

    def test_selection(self):
        na = self.universe.selectAtoms('resname NA+')
        assert_equal(len(na), self.ref_Na_sel_size, "Atom selection of last atoms in file")

    def test_unitcell(self):
        assert_array_almost_equal(self.ts.dimensions, self.ref_unitcell, self.prec,
                                  err_msg="unit cell dimensions (rhombic dodecahedron)")

    def test_volume(self):
        # test_volume: reduce precision for Gromacs comparison to 0 decimals (A**3 <--> nm**3!)
        assert_almost_equal(self.ts.volume, self.ref_volume, 0,
                            err_msg="wrong volume for unitcell (rhombic dodecahedron)")

class TestGROReaderNoConversion(TestCase, RefAdK):
    def setUp(self):
        ##mda.core.flags['convert_gromacs_lengths'] = False
        self.universe = mda.Universe(GRO, convert_units=False)
        self.ts = self.universe.trajectory.ts
        self.prec = 3

    def tearDown(self):
        ##mda.core.flags['convert_gromacs_lengths'] = True  # default
        del self.universe
        del self.ts

    def test_coordinates(self):
        # note: these are the native coordinates in nm; for the test to succeed
        # we loaded with convert_units=False
        A10CA = self.universe.SYSTEM.CA[10]
        assert_almost_equal(A10CA.pos, RefAdK.ref_coordinates['A10CA']/10.0,  # coordinates in nm
                            self.prec,
                            err_msg="wrong native coordinates (in nm) for A10:CA")

    def test_distances(self):
        # 3 decimals on nm in gro but we compare to the distance
        # computed from the pdb file, so the effective precision is 2 again.
        # (Otherwise the distance test fails:
        #  Arrays are not almost equal distance between M1:N and G214:C
        #    ACTUAL: 0.93455122920041123
        #    DESIRED: 0.93513173999999988
        NTERM = self.universe.SYSTEM.N[0]
        CTERM = self.universe.SYSTEM.C[-1]
        d = atom_distance(NTERM, CTERM)
        assert_almost_equal(d, RefAdK.ref_distances['endtoend']/10.0,  # coordinates in nm
                            self.prec - 1,
                            err_msg="distance between M1:N and G214:C")

    def test_unitcell(self):
        # lengths in A : convert to nm
        assert_array_almost_equal(self.ts.dimensions[:3], self.ref_unitcell[:3]/10.0, self.prec,
                                  err_msg="unit cell A,B,C (rhombic dodecahedron)")
        # angles should not have changed
        assert_array_almost_equal(self.ts.dimensions[3:], self.ref_unitcell[3:], self.prec,
                                  err_msg="unit cell alpha,beta,gamma (rhombic dodecahedron)")

    def test_volume(self):
        # ref lengths in A (which was originally converted from nm)
        assert_almost_equal(self.ts.volume, self.ref_volume/1000., 3,
                            err_msg="wrong volume for unitcell (rhombic dodecahedron)")


class TestGROWriter(TestCase):
    def setUp(self):
        self.universe = mda.Universe(GRO)
        self.prec = 2  # 3 decimals in file in nm but MDAnalysis is in A
        ext = ".gro"
        fd, self.outfile = tempfile.mkstemp(suffix=ext)
        fd, self.outfile2 = tempfile.mkstemp(suffix=ext)

    def tearDown(self):
        try:
            os.unlink(self.outfile)
        except OSError:
            pass
        try:
            os.unlink(self.outfile2)
        except OSError:
            pass
        del self.universe

    @dec.slow
    def test_writer(self):
        self.universe.atoms.write(self.outfile)
        u = mda.Universe(self.outfile)
        assert_almost_equal(u.atoms.coordinates(), self.universe.atoms.coordinates(), self.prec,
                            err_msg="Writing GRO file with GROWriter does not reproduce original coordinates")

    @dec.slow
    @attr('issue')
    def test_check_coordinate_limits_min(self):
        """Test that illegal GRO coordinates (x <= -999.9995 nm) are caught with ValueError (Issue 57)"""
        # modify coordinates so we need our own copy or we could mess up parallel tests
        u = mda.Universe(GRO)
        u.atoms[2000].pos[1] = -999.9995 * 10  # nm -> A
        assert_raises(ValueError, u.atoms.write, self.outfile2)
        del u

    @dec.slow
    @attr('issue')
    def test_check_coordinate_limits_max(self):
        """Test that illegal GRO coordinates (x > 9999.9995 nm) are caught with ValueError (Issue 57)"""
        # modify coordinates so we need our own copy or we could mess up parallel tests
        u = mda.Universe(GRO)
        u.atoms[1000].pos[1] = 9999.9999 * 10  # nm -> A  ; [ob] 9999.9996 not caught
        assert_raises(ValueError, u.atoms.write, self.outfile2)
        del u


class TestPDBReaderBig(TestCase, RefAdK):
    def setUp(self):
        self.universe = mda.Universe(PDB)
        self.prec = 6

    def tearDown(self):
        del self.universe

    @dec.slow
    def test_load_pdb(self):
        U = self.universe
        assert_equal(len(U.atoms), self.ref_numatoms, "load Universe from big PDB")
        assert_equal(U.atoms.selectAtoms('resid 150 and name HA2').atoms[0],
                     U.atoms[self.ref_E151HA2_index], "Atom selections")

    @dec.slow
    def test_selection(self):
        na = self.universe.selectAtoms('resname NA+')
        assert_equal(len(na), self.ref_Na_sel_size, "Atom selection of last atoms in file")

    @dec.slow
    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, self.ref_numatoms, "wrong number of atoms")

    @dec.slow
    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, 1, "wrong number of frames")

    @dec.slow
    def test_time(self):
        assert_equal(self.universe.trajectory.time, 0.0, "wrong time of the frame")

    @dec.slow
    def test_frame(self):
        assert_equal(self.universe.trajectory.frame, 0, "wrong frame number")

    @dec.slow
    def test_dt(self):
        """testing that accessing universe.trajectory.dt raises a KeyError for single frame readers"""
        assert_raises(KeyError, self.universe.trajectory.__getattribute__, "dt")

    @dec.slow
    def test_coordinates(self):
        A10CA = self.universe.SYSTEM.CA[10]
        assert_almost_equal(A10CA.pos, self.ref_coordinates['A10CA'], self.prec,
                            err_msg="wrong coordinates for A10:CA")

    @dec.slow
    def test_distances(self):
        NTERM = self.universe.SYSTEM.N[0]
        CTERM = self.universe.SYSTEM.C[-1]
        d = atom_distance(NTERM, CTERM)
        assert_almost_equal(d, self.ref_distances['endtoend'], self.prec,
                            err_msg="wrong distance between M1:N and G214:C")

    @dec.slow
    def test_selection(self):
        na = self.universe.selectAtoms('resname NA+')
        assert_equal(len(na), self.ref_Na_sel_size, "Atom selection of last atoms in file")

    @dec.slow
    @attr('issue')
    def test_unitcell(self):
        assert_array_almost_equal(self.universe.coord.dimensions, self.ref_unitcell, self.prec,
                                  err_msg="unit cell dimensions (rhombic dodecahedron), issue 60")
    @dec.slow
    def test_volume(self):
        assert_almost_equal(self.universe.coord.volume, self.ref_volume, 0,
                            err_msg="wrong volume for unitcell (rhombic dodecahedron)")



@attr('issue')
def TestDCD_Issue32():
    """Test for Issue 32: 0-size dcds lead to a segfault: now caught with IOError"""
    assert_raises(IOError, mda.Universe, PSF, DCD_empty)

class _TestDCD(TestCase):
    def setUp(self):
        self.universe = mda.Universe(PSF, DCD)
        self.dcd = self.universe.trajectory
        self.ts = self.universe.coord

    def tearDown(self):
        del self.universe
        del self.dcd
        del self.ts

class TestDCDReader(_TestDCD):
    def test_rewind_dcd(self):
        self.dcd.rewind()
        assert_equal(self.ts.frame, 1, "rewinding to frame 1")

    def test_next_dcd(self):
        self.dcd.rewind()
        self.dcd.next()
        assert_equal(self.ts.frame, 2, "loading frame 2")

    def test_jump_dcd(self):
        self.dcd[15]  # index is 0-based but frames are 1-based
        assert_equal(self.ts.frame, 16, "jumping to frame 16")

    def test_jump_lastframe_dcd(self):
        self.dcd[-1]
        assert_equal(self.ts.frame, 98, "indexing last frame with dcd[-1]")

    def test_slice_dcd(self):
        frames = [ts.frame for ts in self.dcd[5:17:3]]
        assert_equal(frames, [6, 9, 12, 15], "slicing dcd [5:17:3]")

    def test_reverse_dcd(self):
        frames = [ts.frame for ts in self.dcd[20:5:-1]]
        assert_equal(frames, range(21,6,-1), "reversing dcd [20:5:-1]")

    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, 3341, "wrong number of atoms")

    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, 98, "wrong number of frames in dcd")

    def test_dt(self):
        assert_almost_equal(self.universe.trajectory.dt, 1.0, 4,
                            err_msg="wrong timestep dt")

    def test_totaltime(self):
        # test_totaltime(): need to reduce precision because dt is only precise
        # to ~4 decimals and accumulating the inaccuracy leads to even lower
        # precision in the totaltime (consequence of fixing Issue 64)
        assert_almost_equal(self.universe.trajectory.totaltime, 98.0, 3,
                            err_msg="wrong total length of AdK trajectory")

    def test_frame(self):
        self.dcd[15]  # index is 0-based but frames are 1-based
        assert_equal(self.universe.trajectory.frame, 16, "wrong frame number")

    def test_time(self):
        self.dcd[15]  # index is 0-based but frames are 1-based
        assert_almost_equal(self.universe.trajectory.time, 16.0, 5,
                            err_msg="wrong time of frame")

    def test_volume(self):
        assert_almost_equal(self.ts.volume, 0.0, 3,
                            err_msg="wrong volume for unitcell (no unitcell in DCD so this should be 0)")


class TestDCDWriter(TestCase):
    def setUp(self):
        self.universe = mda.Universe(PSF, DCD)
        ext = ".dcd"
        fd, self.outfile = tempfile.mkstemp(suffix=ext)
        self.Writer = MDAnalysis.coordinates.DCD.DCDWriter

    def tearDown(self):
        try:
            os.unlink(self.outfile)
        except OSError:
            pass
        del self.universe
        del self.Writer

    @attr('issue')
    def test_write_trajectory(self):
        """Test writing DCD trajectories (Issue 50)"""
        t = self.universe.trajectory
        W = self.Writer(self.outfile, t.numatoms, delta=t.delta, step=t.skip_timestep)
        for ts in self.universe.trajectory:
            W.write_next_timestep(ts)
        W.close()

        uw = mda.Universe(PSF, self.outfile)

        # check that the coordinates are identical for each time step
        for orig_ts, written_ts in itertools.izip(self.universe.trajectory, uw.trajectory):
            assert_array_almost_equal(written_ts._pos, orig_ts._pos, 3,
                                      err_msg="coordinate mismatch between original and written trajectory at frame %d (orig) vs %d (written)" % (orig_ts.frame, written_ts.frame))

    def test_OtherWriter(self):
        t = self.universe.trajectory
        W = t.OtherWriter(self.outfile)
        for ts in self.universe.trajectory:
            W.write_next_timestep(ts)
        W.close()

        uw = mda.Universe(PSF, self.outfile)

        # check that the coordinates are identical for each time step
        for orig_ts, written_ts in itertools.izip(self.universe.trajectory, uw.trajectory):
            assert_array_almost_equal(written_ts._pos, orig_ts._pos, 3,
                                      err_msg="coordinate mismatch between original and written trajectory at frame %d (orig) vs %d (written)" % (orig_ts.frame, written_ts.frame))



class TestDCDWriter_Issue59(TestCase):
    def setUp(self):
        """Generate input xtc."""
        self.u = MDAnalysis.Universe(PSF,DCD)
        fd, self.xtc = tempfile.mkstemp(suffix='.xtc')
        wXTC = MDAnalysis.Writer(self.xtc, self.u.atoms.numberOfAtoms())
        for ts in self.u.trajectory:
            wXTC.write(ts);
        wXTC.close()

    def tearDown(self):
        try:
            os.unlink(self.xtc)
        except OSError:
            pass
        try:
            os.unlink(self.dcd)
        except (AttributeError, OSError):
            pass
        del self.u

    @attr('issue')
    def test_issue59(self):
        """Test writing of XTC to DCD (Issue 59)"""
        xtc = MDAnalysis.Universe(PSF, self.xtc)
        fd, self.dcd = tempfile.mkstemp(suffix='.dcd')
        wDCD = MDAnalysis.Writer(self.dcd, xtc.atoms.numberOfAtoms())
        for ts in xtc.trajectory:
            wDCD.write(ts);
        wDCD.close()

        dcd = MDAnalysis.Universe(PSF, self.dcd)

        xtc.trajectory.rewind()
        dcd.trajectory.rewind()

        assert_array_almost_equal(xtc.atoms.coordinates(), dcd.atoms.coordinates(), 3,
                                  err_msg="XTC -> DCD: DCD coordinates are messed up (Issue 59)")

    def test_OtherWriter(self):
        dcd = self.u
        wXTC = dcd.trajectory.OtherWriter(self.xtc)
        for ts in dcd.trajectory:
            wXTC.write(ts)
        wXTC.close()

        xtc = MDAnalysis.Universe(PSF, self.xtc)
        xtc.trajectory.rewind()
        dcd.trajectory.rewind()

        assert_array_almost_equal(dcd.atoms.coordinates(), xtc.atoms.coordinates(), 2,
                                  err_msg="DCD -> XTC: coordinates are messed up (frame %d)" % dcd.trajectory.frame)
        xtc.trajectory[3]
        dcd.trajectory[3]
        assert_array_almost_equal(dcd.atoms.coordinates(), xtc.atoms.coordinates(), 2,
                                  err_msg="DCD -> XTC: coordinates are messed up (frame %d)" % dcd.trajectory.frame)


class TestDCDCorrel(_TestDCD):
    def setUp(self):
        # Note: setUp is executed for *every* test !
        super(TestDCDCorrel, self).setUp()
        import MDAnalysis.core.Timeseries as TS
        self.collection = TS.TimeseriesCollection()
        C = self.collection
        all = self.universe.atoms
        ca = self.universe.s4AKE.CA
        ca_termini =  mda.core.AtomGroup.AtomGroup([ca[0], ca[-1]])
        # note that this is not quite phi... HN should be C of prec. residue
        phi151 = self.universe.selectAtoms('resid 151').selectAtoms('name HN', 'name N', 'name CA', 'name CB')
        C.addTimeseries(TS.Atom('v', ca_termini))       # 0
        C.addTimeseries(TS.Bond(ca_termini))            # 1
        C.addTimeseries(TS.Bond([ca[0], ca[-1]]))       # 2
        C.addTimeseries(TS.Angle(phi151[1:4]))          # 3
        C.addTimeseries(TS.Dihedral(phi151))            # 4
        C.addTimeseries(TS.Distance('r', ca_termini))   # 5
        C.addTimeseries(TS.CenterOfMass(ca))            # 6
        C.addTimeseries(TS.CenterOfGeometry(ca))        # 7
        C.addTimeseries(TS.CenterOfMass(all))           # 8
        C.addTimeseries(TS.CenterOfGeometry(all))       # 9
        # cannot test WaterDipole because there's no water in the test dcd
        C.compute(self.dcd)

    def tearDown(self):
        del self.collection
        super(TestDCDCorrel, self).tearDown()

    def test_correl(self):
        assert_equal(len(self.collection), 10, "Correl: len(collection)")

    def test_Atom(self):
        assert_equal(self.collection[0].shape, (2, 3, 98),
                     "Correl: Atom positions")

    def test_Bonds(self):
        C = self.collection
        assert_array_equal(C[1].__data__, C[2].__data__,
                           "Correl: Bonds with lists and AtomGroup")

    def test_Angle(self):
        C = self.collection
        avg_angle = 1.9111695972912988
        assert_almost_equal(C[3].__data__.mean(), avg_angle,
                            err_msg="Correl: average Angle")

    def test_Dihedral(self):
        C = self.collection
        avg_phi151 = 0.0088003870749735619
        assert_almost_equal(C[4].__data__.mean(), avg_phi151,
                            err_msg="Correl: average Dihedral")

    def test_scalarDistance(self):
        C = self.collection
        avg_dist = 9.7960210987736236
        assert_almost_equal(C[5].__data__.mean(), avg_dist,
                            err_msg="Correl: average scalar Distance")

    def test_CenterOfMass(self):
        C = self.collection
        avg_com_ca  = np.array([ 0.0043688 , -0.27812258, 0.0284051])
        avg_com_all = np.array([-0.10086529, -0.16357276, 0.12724672])
        assert_array_almost_equal(C[6].__data__.mean(axis=1), avg_com_ca,
                                  err_msg="Correl: average CA CenterOfMass")
        assert_almost_equal(C[8].__data__.mean(axis=1), avg_com_all,
                            err_msg="Correl: average all CenterOfMass")

    def test_CenterOfGeometry(self):
        C = self.collection
        avg_cog_all = np.array([-0.13554797, -0.20521885, 0.2118998])
        assert_almost_equal(C[9].__data__.mean(axis=1), avg_cog_all,
                            err_msg="Correl: average all CenterOfGeometry")

    def test_CA_COMeqCOG(self):
        C = self.collection
        assert_array_almost_equal(C[6].__data__, C[7].__data__,
                                  err_msg="Correl: CA CentreOfMass == CenterOfGeometry")

    def test_clear(self):
        C = self.collection
        C.clear()
        assert_equal(len(C), 0, "Correl: clear()")

# notes:
def compute_correl_references():
    universe = MDAnalysis.Universe(PSF,DCD)

    all = universe.atoms
    ca = universe.s4AKE.CA
    ca_termini =  mda.core.AtomGroup.AtomGroup([ca[0], ca[-1]])
    phi151 = universe.selectAtoms('resid 151').selectAtoms('name HN', 'name N', 'name CA', 'name CB')

    C = MDAnalysis.collection
    C.clear()

    C.addTimeseries(TS.Atom('v', ca_termini))       # 0
    C.addTimeseries(TS.Bond(ca_termini))            # 1
    C.addTimeseries(TS.Bond([ca[0], ca[-1]]))       # 2
    C.addTimeseries(TS.Angle(phi151[1:4]))          # 3
    C.addTimeseries(TS.Dihedral(phi151))            # 4
    C.addTimeseries(TS.Distance('r', ca_termini))   # 5
    C.addTimeseries(TS.CenterOfMass(ca))            # 6
    C.addTimeseries(TS.CenterOfGeometry(ca))        # 7
    C.addTimeseries(TS.CenterOfMass(all))           # 8
    C.addTimeseries(TS.CenterOfGeometry(all))       # 9

    C.compute(universe.dcd)

    results = {"avg_angle": C[3].__data__.mean(),
               "avg_phi151": C[4].__data__.mean(),
               "avg_dist": C[5].__data__.mean(),
               "avg_com_ca": C[6].__data__.mean(axis=1),
               "avg_com_all": C[8].__data__.mean(axis=1),
               "avg_cog_all": C[9].__data__.mean(axis=1),
               }
    C.clear()
    return results

class TestChainReader(TestCase):
    def setUp(self):
        self.universe = mda.Universe(PSF, [DCD,CRD,DCD,CRD,DCD,CRD,CRD])
        self.trajectory = self.universe.trajectory

    def test_next_trajectory(self):
        self.trajectory.rewind()
        self.trajectory.next()
        assert_equal(self.trajectory.ts.frame, 2, "loading frame 2")

    def test_numatoms(self):
        assert_equal(self.universe.trajectory.numatoms, 3341, "wrong number of atoms")

    def test_numframes(self):
        assert_equal(self.universe.trajectory.numframes, 3*98 + 4, "wrong number of frames in chained dcd")

    def test_iteration(self):
        for ts in self.trajectory:
            pass # just forward to last frame
        assert_equal(self.trajectory.numframes, ts.frame,
                     "iteration yielded wrong number of frames (%d), should be %d" \
                         % (ts.frame, self.trajectory.numframes))

    def test_jump_lastframe_trajectory(self):
        self.trajectory[-1]
        print self.trajectory.ts, self.trajectory.ts.frame
        assert_equal(self.trajectory.ts.frame, self.trajectory.numframes, "indexing last frame with trajectory[-1]")

    @dec.knownfailureif(True, "slicing not implemented for chained reader")
    def test_slice_trajectory(self):
        frames = [ts.frame for ts in self.trajectory[5:17:3]]
        assert_equal(frames, [6, 9, 12, 15], "slicing dcd [5:17:3]")

    def test_frame_numbering(self):
        self.trajectory[98]  # index is 0-based but frames are 1-based
        assert_equal(self.universe.trajectory.frame, 99, "wrong frame number")

    def test_frame(self):
        self.trajectory[0]
        coord0 = self.universe.atoms.coordinates().copy()
        # forward to frame where we repeat original dcd again:
        # dcd:0..97 crd:98 dcd:99..196
        self.trajectory[99]
        assert_array_equal(self.universe.atoms.coordinates(), coord0,
                           "coordinates at frame 1 and 100 should be the same!")

    @dec.knownfailureif(True, "time attribute not implemented for chained reader")
    def test_time(self):
        self.trajectory[30]  # index is 0-based but frames are 1-based
        assert_almost_equal(self.universe.trajectory.time, 31.0, 5,
                            err_msg="wrong time of frame")


class _GromacsReader(TestCase):
    # This base class assumes same lengths and dt for XTC and TRR test cases!
    filename = None
    ref_unitcell = np.array([ 80.017,  80.017,  80.017,  60., 60., 90.], dtype=np.float32)
    ref_volume = 362270.0  # computed with Gromacs: 362.26999999999998 nm**3 * 1000 A**3/nm**3

    def setUp(self):
        # default flag--just make sure!... but can lead to race conditions
        # use explicit convert_units argument to specify behaviour
        ##mda.core.flags['convert_gromacs_lengths'] = True
        # loading from GRO is 4x faster than the PDB reader
        self.universe = mda.Universe(GRO, self.filename, convert_units=True)
        self.trajectory = self.universe.trajectory
        self.prec = 3
        self.ts = self.universe.coord
        # dummy output file
        ext = os.path.splitext(self.filename)[1]
        fd, self.outfile = tempfile.mkstemp(suffix=ext)

    def tearDown(self):
        try:
            os.unlink(self.outfile)
        except:
            pass
        del self.universe

    @dec.slow
    def test_flag_convert_gromacs_lengths(self):
        assert_equal(mda.core.flags['convert_gromacs_lengths'], True,
                     "MDAnalysis.core.flags['convert_gromacs_lengths'] should be True by default")

    @dec.slow
    def test_rewind_xdrtrj(self):
        self.trajectory.rewind()
        assert_equal(self.ts.frame, 1, "rewinding to frame 1")

    @dec.slow
    def test_next_xdrtrj(self):
        self.trajectory.rewind()
        self.trajectory.next()
        assert_equal(self.ts.frame, 2, "loading frame 2")

    @dec.slow
    def test_jump_xdrtrj(self):
        self.trajectory[4]  # index is 0-based but frames are 1-based
        assert_equal(self.ts.frame, 5, "jumping to frame 5")

    @dec.slow
    def test_jump_lastframe_xdrtrj(self):
        self.trajectory[-1]
        assert_equal(self.ts.frame, 10, "indexing last frame with trajectory[-1]")

    @dec.slow
    def test_slice_xdrtrj(self):
        frames = [ts.frame for ts in self.trajectory[2:9:3]]
        assert_equal(frames,  [3, 6, 9], "slicing xdrtrj [2:9:3]")

    @dec.slow
    @dec.knownfailureif(True, "XTC/TRR reverse slicing not implemented for performance reasons")
    def test_reverse_xdrtrj(self):
        frames = [ts.frame for ts in self.trajectory[::-1]]
        assert_equal(frames, range(10,0,-1), "slicing xdrtrj [::-1]")

    @dec.slow
    def test_coordinates(self):
        ca_nm = np.array([[ 6.043369675,  7.385184479,  1.381425762]], dtype=np.float32)
        # coordinates in the base unit (needed for True)
        ca_Angstrom = ca_nm * 10.0
        U = self.universe
        T = U.trajectory
        T.rewind()
        T.next()
        T.next()
        assert_equal(self.ts.frame, 3, "failed to step to frame 3")
        ca = U.selectAtoms('name CA and resid 122')
        # low precision match (2 decimals in A, 3 in nm) because the above are the trr coords
        assert_array_almost_equal(ca.coordinates(), ca_Angstrom, 2,
                                  err_msg="coords of Ca of resid 122 do not match for frame 3")

    @dec.slow
    @attr('issue')
    def test_unitcell(self):
        """Test that xtc/trr unitcell is read correctly (Issue 34)"""
        self.universe.trajectory.rewind()
        uc = self.ts.dimensions
        assert_array_almost_equal(uc, self.ref_unitcell, self.prec, err_msg="unit cell dimensions (rhombic dodecahedron)")

    @dec.slow
    def test_volume(self):
        # need to reduce precision for test (nm**3 <--> A**3)
        self.universe.trajectory.rewind()
        vol = self.ts.volume
        assert_array_almost_equal(vol, self.ref_volume, 0, err_msg="unit cell volume (rhombic dodecahedron)")

    @dec.slow
    def test_dt(self):
        assert_almost_equal(self.universe.trajectory.dt, 100.0, 4,
                            err_msg="wrong timestep dt")

    @dec.slow
    def test_totaltime(self):
        # test_totaltime(): need to reduce precision because dt is only precise
        # to ~4 decimals and accumulating the inaccuracy leads to even lower
        # precision in the totaltime (consequence of fixing Issue 64)
        assert_almost_equal(self.universe.trajectory.totaltime, 1000.0, 3,
                            err_msg="wrong total length of trajectory")

    @dec.slow
    def test_frame(self):
        self.trajectory[4]  # index is 0-based but frames are 1-based
        assert_equal(self.universe.trajectory.frame, 5, "wrong frame number")

    @dec.slow
    def test_time(self):
        self.trajectory[4]  # index is 0-based but frames are 1-based
        assert_almost_equal(self.universe.trajectory.time, 500.0, 5,
                            err_msg="wrong time of frame")

    @dec.slow
    def test_get_Writer(self):
        W = self.universe.trajectory.Writer(self.outfile)
        assert_equal(self.universe.trajectory.format, W.format)
        assert_equal(self.universe.atoms.numberOfAtoms(), W.numatoms)
        W.close()

    @dec.slow
    def test_Writer(self):
        W = self.universe.trajectory.Writer(self.outfile)
        W.write(self.universe.atoms)
        self.universe.trajectory.next()
        W.write(self.universe.atoms)
        W.close()
        self.universe.trajectory.rewind()
        u = MDAnalysis.Universe(GRO, self.outfile)
        assert_equal(u.trajectory.numframes, 2)
        # prec = 6: TRR test fails; here I am generous and take self.prec = 3...
        assert_almost_equal(u.atoms.coordinates(), self.universe.atoms.coordinates(), self.prec)

class TestXTCReader(_GromacsReader):
    filename = XTC

class TestTRRReader(_GromacsReader):
    filename = TRR


class _XDRNoConversion(TestCase):
    filename = None
    def setUp(self):
        # not needed when using convert_units=False
        ##mda.core.flags['convert_gromacs_lengths'] = False
        self.universe = mda.Universe(PDB, self.filename, convert_units=False)
        self.ts = self.universe.trajectory.ts
    def tearDown(self):
        ##mda.core.flags['convert_gromacs_lengths'] = True  # default
        del self.universe
        del self.ts

    @dec.slow
    def test_coordinates(self):
        # note: these are the native coordinates in nm; for the test to succeed:
        ##assert_equal(mda.core.flags['convert_gromacs_lengths'], False,
        ##             "oops, mda.core.flags['convert_gromacs_lengths'] should be False for this test")
        ca_nm = np.array([[ 6.043369675,  7.385184479,  1.381425762]], dtype=np.float32)
        U = self.universe
        T = U.trajectory
        T.rewind()
        T.next()
        T.next()
        assert_equal(self.ts.frame, 3, "failed to step to frame 3")
        ca = U.selectAtoms('name CA and resid 122')
        # low precision match because we also look at the trr: only 3 decimals in nm in xtc!
        assert_array_almost_equal(ca.coordinates(), ca_nm, 3,
                                  err_msg="native coords of Ca of resid 122 do not match for frame 3 "\
                                      "with convert_units=False")

class TestXTCNoConversion(_XDRNoConversion):
    filename = XTC

class TestTRRNoConversion(_XDRNoConversion):
    filename = TRR

class _GromacsWriter(TestCase):
    infilename = None  # XTC or TRR
    Writers = {'.trr': MDAnalysis.coordinates.TRR.TRRWriter,
               '.xtc': MDAnalysis.coordinates.XTC.XTCWriter,
               }

    def setUp(self):
        self.universe = mda.Universe(GRO, self.infilename)
        ext = os.path.splitext(self.infilename)[1]
        fd, self.outfile = tempfile.mkstemp(suffix=ext)
        self.Writer = self.Writers[ext]

    def tearDown(self):
        try:
            os.unlink(self.outfile)
        except:
            pass
        del self.universe
        del self.Writer

    @dec.slow
    @attr('issue')
    def test_write_trajectory(self):
        """Test writing Gromacs trajectories (Issue 38)"""
        t = self.universe.trajectory
        W = self.Writer(self.outfile, t.numatoms, delta=t.delta, step=t.skip_timestep)
        for ts in self.universe.trajectory:
            W.write_next_timestep(ts)
        W.close()

        uw = mda.Universe(GRO, self.outfile)

        # check that the coordinates are identical for each time step
        for orig_ts, written_ts in itertools.izip(self.universe.trajectory, uw.trajectory):
            assert_array_almost_equal(written_ts._pos, orig_ts._pos, 3,
                                      err_msg="coordinate mismatch between original and written trajectory at frame %d (orig) vs %d (written)" % (orig_ts.frame, written_ts.frame))

class TestXTCWriter(_GromacsWriter):
    infilename = XTC

class TestTRRWriter(_GromacsWriter):
    infilename = TRR

@attr('issue')
def test_triclinic_box():
    """Test coordinates.core.triclinic_box() (Issue 61)"""
    unitcell = np.array([80.017,   55,   100.11,  60.00,  30.50,  90.00])
    box = MDAnalysis.coordinates.core.triclinic_vectors(unitcell)
    new_unitcell = MDAnalysis.coordinates.core.triclinic_box(box[0],box[1],box[2])
    assert_array_almost_equal(new_unitcell, unitcell, 3,
                              err_msg="unitcell round-trip connversion failed (Issue 61)")


