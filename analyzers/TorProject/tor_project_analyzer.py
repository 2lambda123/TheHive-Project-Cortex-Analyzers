#!/usr/bin/env python
from cortexutils.analyzer import Analyzer
import tor_project


class TorProjectAnalyzer(Analyzer):
    """Cortex analyzer to query TorProject for exit nodes IP addresses"""
    def __init__(self):
        Analyzer.__init__(self)
        self.ttl = self.getParam('config.ttl', 84600)
        self.cache_duration = self.getParam('config.cache.duration', 3600)
        self.cache_root = self.getParam(
            'config.cache.root', '/tmp/cortex/tor_project'
        )

        self.client = tor_project.TorProjectClient(
            ttl=self.ttl,
            cache_duration=self.cache_duration,
            cache_root=self.cache_root
        )

    def summary(self, raw):
        taxonomies = []
        level = 'info'
        value = 'false'
        if ("results" in raw):
            r = len(raw['results'])
            if r > 0:
                level = 'suspicious'
                value = 'true'
        taxonomies.append(
            self.build_taxonomy(level, 'TorProject', 'Node', value))
        return taxonomies

    def run(self):
        if self.data_type != 'ip':
            return self.error('Not an IP address')
        report = self.client.query(self.get_data())
        self.report({'results': report})


if __name__ == '__main__':
    TorProjectAnalyzer().run()
