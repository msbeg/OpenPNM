import OpenPNM as op
import numpy as np


class InvasionPercolationTest:

    def setup_class(self):
        # Create Topological Network object
        self.wrk = op.Base.Workspace()
        self.wrk.loglevel = 50
        N = 10
        self.net = op.Network.Cubic(shape=[N, N, 1], spacing=1, name='net')
        self.net.add_boundaries()
        self.net.trim(self.net.pores('bottom_boundary'))
        self.net.trim(self.net.pores('top_boundary'))
        # Create Geometry object for internal pores
        Ps = self.net.pores('boundary', mode='not')
        Ts = self.net.find_neighbor_throats(pores=Ps,
                                            mode='intersection',
                                            flatten=True)
        self.geom = op.Geometry.Stick_and_Ball(network=self.net,
                                               pores=Ps,
                                               throats=Ts)
        # Create Geometry object for boundary pores
        Ps = self.net.pores('boundary')
        Ts = self.net.find_neighbor_throats(pores=Ps, mode='not_intersection')
        self.boun = op.Geometry.Boundary(network=self.net, pores=Ps, throats=Ts)
        self.phase = op.Phases.Water(network=self.net, name='water')
        # Create one Physics object for each phase
        Ps = self.net.pores()
        Ts = self.net.throats()
        self.phys = op.Physics.Standard(network=self.net,
                                        phase=self.phase,
                                        pores=Ps,
                                        throats=Ts)
        # 2. Perform Invasion Percolation
        step = 1
        inlets = self.net.pores('front_boundary')
        ip_inlets = [inlets[x] for x in range(0, len(inlets), step)]
        self.alg = op.Algorithms.InvasionPercolation(network=self.net)
        self.alg.run(phase=self.phase, inlets=ip_inlets)
        self.alg.return_results()

    def test_apply_trapping(self):
        import time
        t1 = time.time()
        outlets = self.net.pores(['back_boundary',
                                  'left_boundary',
                                  'right_boundary'])
        self.alg.apply_trapping(outlets)
        t2 = time.time()
        self.alg.trapping_slow(outlets)
        t3 = time.time()
        assert (t2-t1) < (t3-t2)
        bulk = self.net.pores('boundary', mode='not')
        assert np.allclose(self.alg['pore.trapped'][bulk],
                           (self.alg['pore.trapped_slow'] != -1)[bulk])
