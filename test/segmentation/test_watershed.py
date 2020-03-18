import unittest
import numpy as np
try:
    import vigra
except ImportError:
    vigra = None
try:
    import nifty
except ImportError:
    nifty = None


class TestWatershed(unittest.TestCase):

    @unittest.skipUnless(vigra, "Need vigra for watershed functionality")
    def test_size_filter(self):
        from elf.segmentation.watershed import apply_size_filter
        shape = (10, 256, 256)
        seg = np.random.randint(0, 1000, size=shape, dtype='uint32')
        inp = np.random.rand(*shape).astype('float32')
        size_filter = 5000
        seg_filtered, max_id = apply_size_filter(seg, inp, size_filter)
        self.assertEqual(max_id, seg_filtered.max())
        _, counts = np.unique(seg_filtered, return_counts=True)
        self.assertGreaterEqual(size_filter, counts.min())

    @unittest.skipUnless(vigra, "Need vigra for watershed functionality")
    def test_watershed(self):
        from elf.segmentation.watershed import watershed

        shape = (10, 256, 256)
        inp = np.random.rand(*shape).astype('float32')
        seeds = np.zeros(shape, dtype='uint32')

        seed_ids = list(range(1, 100))
        seed_points = np.random.choice(seeds.size, size=(len(seed_ids),), replace=False)
        coords = np.unravel_index(seed_points, shape)
        seeds[coords] = seed_ids

        seg, max_id = watershed(inp, seeds)
        self.assertEqual(max_id, max(seed_ids))
        self.assertEqual(max_id, seg.max())

        seg_ids = set(np.unique(seg))
        self.assertEqual(seg_ids, set(seed_ids))

    @unittest.skipUnless(vigra, "Need vigra for watershed functionality")
    def test_distance_transform_watershed_3d(self):
        from elf.segmentation.watershed import distance_transform_watershed
        shape = (32, 128, 128)
        inp = np.random.rand(*shape).astype('float32')

        # test for different options
        configs = [{'sigma_seeds': 2.},
                   {'sigma_seeds': 2., 'pixel_pitch': (1, 1, 1)},
                   {'sigma_seeds': 2., 'pixel_pitch': (4, 1, 1)},
                   {'sigma_seeds': 0., 'sigma_weights': 0., 'min_size': 0}]
        for config in configs:
            ws, max_id = distance_transform_watershed(inp, threshold=.5, **config)
            self.assertEqual(inp.shape, ws.shape)
            # make sure result is non-trivial
            self.assertGreater(max_id, 32)
            self.assertEqual(ws.max(), max_id)
            self.assertNotIn(0, ws)

    @unittest.skipUnless(vigra, "Need vigra for watershed functionality")
    def test_distance_transform_watershed_2d(self):
        from elf.segmentation.watershed import distance_transform_watershed
        shape = (256, 256)
        inp = np.random.rand(*shape).astype('float32')

        # test for different options
        configs = [{'sigma_seeds': 2.},
                   {'sigma_seeds': 2., 'pixel_pitch': (1, 1)},
                   {'sigma_seeds': 2., 'pixel_pitch': (4, 2)},
                   {'sigma_seeds': 0., 'sigma_weights': 0., 'min_size': 0}]
        for config in configs:
            ws, max_id = distance_transform_watershed(inp, threshold=.5, **config)
            self.assertEqual(inp.shape, ws.shape)
            # make sure result is non-trivial
            self.assertGreater(max_id, 32)
            self.assertEqual(ws.max(), max_id)
            self.assertNotIn(0, ws)

    @unittest.skipUnless(vigra and nifty,
                         "Need vigra and nifty for watershed with non-max suppression")
    def test_distance_transform_watershed_suppression(self):
        from elf.segmentation.watershed import distance_transform_watershed
        shape = (256, 256)
        inp = np.random.rand(*shape).astype('float32')

        ws, max_id = distance_transform_watershed(inp, threshold=.5, sigma_seeds=2.,
                                                  apply_nonmax_suppression=True)
        self.assertEqual(inp.shape, ws.shape)
        # make sure result is non-trivial
        self.assertGreater(max_id, 32)
        self.assertEqual(ws.max(), max_id)
        self.assertNotIn(0, ws)

    @unittest.skipUnless(vigra, "Need vigra for watershed functionality")
    def test_stacked_watershed(self):
        from elf.segmentation.watershed import stacked_watershed
        shape = (32, 256, 256)
        inp = np.random.rand(*shape).astype('float32')

        ws, max_id = stacked_watershed(inp, threshold=.5, sigma_seeds=2.)
        self.assertEqual(inp.shape, ws.shape)
        # make sure result is non-trivial
        self.assertGreater(max_id, 256)
        self.assertEqual(ws.max(), max_id)
        self.assertNotIn(0, ws)


if __name__ == '__main__':
    unittest.main()
