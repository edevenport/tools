#!/usr/bin/python

import os
import json
import requests
import sys
import yaml

from requests.auth import HTTPBasicAuth


def main():
    filename = parse_argument()
    organizations = load_file(filename)

    print 'Organization,Repository,Watchers,Stars,Forks,Downloads,Views,' \
          'Total Visitors,Clones,PyPI,RubyGems,Packagist,PuppetForge,Nuget'

    for org_name in organizations:
        for project in organizations[org_name]:
            github_stats = None
            package_stats = {}

            github_stats = get_github_stats(org_name, project['repo'])

            if [site for site in project.keys() if site in SITES]:
                package_stats[site] = get_package_stats(org_name,
                                                        project[site],
                                                        site)

            print '{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}'.format(
                org_name,
                project['repo'],
                github_stats.get('subscribers'),
                github_stats.get('stargazers'),
                github_stats.get('forks'),
                github_stats.get('downloads'),
                github_stats.get('views'),
                github_stats.get('unique_visitors'),
                github_stats.get('clones'),
                package_stats.get('pypi'),
                package_stats.get('rubygems'),
                package_stats.get('packagist'),
                package_stats.get('puppetforge'),
                package_stats.get('nuget')
            )


def get_github_stats(org, repo):
    stats = {}
    endpoints = {
        'repo': '',
        'traffic': '/traffic/views',
        'clones': '/traffic/clones',
        'releases': '/releases',
    }
    auth = HTTPBasicAuth(USERNAME, PASSWORD)

    for key, endpoint in endpoints.items():
        url = 'https://api.github.com/repos/{0}/{1}{2}'.format(org,
                                                               repo,
                                                               endpoint)
        results = session.get(url, auth=auth)
        if results.status_code == 200:
            results = json.loads(results.text)

            if key is 'repo':
                stats['subscribers'] = results.get('subscribers_count')
                stats['stargazers'] = results.get('stargazers_count')
                stats['forks'] = results.get('forks_count')

            if key is 'traffic':
                print "VIEWS"
                stats['views'] = results.get('count')
                print stats['views']
                stats['unique_visitors'] = results.get('uniques')

            if key is 'clones':
                stats['clones'] = results.get('count')

            if key is 'releases':
                count = 0
                for release in results:
                    for asset in release.get('assets'):
                        count += asset['download_count']
                stats['downloads'] = count
        else:
            continue

    return stats


def get_package_stats(org=None, package=None, site=None):
    endpoints = {
        'pypi': 'https://pypi.python.org/pypi/{package}/json',
        'rubygems': 'https://rubygems.org/api/v1/gems/{package}.json',
        'packagist': 'https://packagist.org/packages/{org}/{package}.json',
        'puppetforge': 'https://forgeapi.puppetlabs.com/v3/modules/{package}',
        'nuget': 'https://api-v2v3search-0.nuget.org/query?q=packageid:{package}'
    }

    url = endpoints[site].format(org=org, package=package)
    results = session.get(url)
    results = json.loads(results.text)

    if site == 'pypi':
        count = 0
        for version in results['releases']:
            release = results['releases'].get(version)
            if len(release) == 1:
                count += release[0]['downloads']
        return count

    if site == 'rubygems':
        return results['downloads']

    if site == 'packagist':
        return results['package']['downloads']['total']

    if site == 'puppetforge':
        return results['downloads']

    if site == 'nuget':
        return results['data'][0]['totalDownloads']


def load_file(filename):
    with open(filename, 'r') as stream:
        try:
            return yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def parse_argument():
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if os.path.exists(filename):
            return filename
        else:
            print('File not found: {0}'.format(filename))
            exit(1)
    else:
        print('Missing argument.')
        exit(1)


if __name__ == '__main__':
    # GitHub variables
    LOGIN_URL = 'https://github.com/login'
    SESSION_URL = 'https://github.com/session'

    # Package repository variables
    SITES = ['pypi', 'rubygems', 'packagist', 'puppetforge', 'nuget']

    # Credentials
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')

    # Initiate HTTP session
    session = requests.session()

    main()
