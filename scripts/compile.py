#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from build_pack_utils import Builder


def memory_limit_to_int_mb(mem_limit_str):
    mem = int(mem_limit_str[:-1])
    if mem_limit_str[-1:] == 'g':
        mem = mem * 1024
    return mem


def configure_catalina_opts(ctx):
    if 'CATALINA_OPTS' in os.environ.keys():
        ctx['CATALINA_OPTS'] = os.environ['CATALINA_OPTS']
    if 'CATALINA_OPTS' not in ctx.keys():
        memory_limit = memory_limit_to_int_mb(ctx['MEMORY_LIMIT'])
        xmx = int(memory_limit * 0.6)
        perm = int(memory_limit * 0.2)
        ctx['CATALINA_OPTS'] = ' '.join((
            '-Xmx%d%s' % (xmx, 'm'),
            '-Xms%d%s' % (xmx, 'm'),
            '-Xss256k',
            '-XX:MaxPermSize=%d%s' % (perm, 'm'),
            '-Dlogs.dir=%s' % ctx['LOG_DIR']))
    if ctx['CATALINA_OPTS'].find('-Djava.io.tempdir') == -1:
        ctx['CATALINA_OPTS'] += '-Djava.io.tempdir=$TMPDIR'
    if ctx['CATALINA_OPTS'].find('-Dlogs.dir') == -1:
        ctx['CATALINA_OPTS'] += '-Dlogs.dir=%s' % ctx['LOG_DIR']
    if ctx['CATALINA_OPTS'].find('-Dhttp.port') == -1:
        ctx['CATALINA_OPTS'] += '-Dhttp.port=$VCAP_APP_PORT'


def log_run(cmd, retcode, stdout, stderr):
    print 'Comand %s completed with [%d]' % (str(cmd), retcode)
    print 'STDOUT:'
    print stdout
    print 'STDERR:'
    print stderr
    if retcode != 0:
        raise RuntimeError('Script Failure')


if __name__ == '__main__':
    (Builder()
        .configure()
            .default_config()
            .user_config()
            .done()
        .install()
            .package('JAVA')
            .package('TOMCAT')
            .config()
                .all_files()
                .from_application('config/tomcat')
                .or_from_build_pack('defaults/config')
                .to('tomcat/conf')
                .done()
            .done()
        .execute()
            .method(configure_catalina_opts)
        .create_start_script()
            .environment_variable()
                .export()
                .name('JAVA_HOME')
                .value('JAVA_INSTALL_PATH')
            .command()
                .run('$HOME/tomcat/bin/catalina.sh run -security')
                .done()
            .write())
