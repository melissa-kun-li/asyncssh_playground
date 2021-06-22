import asyncio, asyncssh, asyncssh.logging
import logging
from io import StringIO
from shlex import quote
from asyncssh.misc import async_context_manager


asyncssh_logger = logging.getLogger()
asyncssh.logging.set_log_level(logging.DEBUG)

# create handler with StringIO object
log_string = StringIO()
ch = logging.StreamHandler(log_string)
ch.setLevel(logging.DEBUG)

# add handler to logger
asyncssh_logger.addHandler(ch)


class SSHConnection:
    def __init__(self):
        self.connection = None

    async def _remote_connection(self):
        try:
            # need known_hosts=None else will get "Host key is not trusted" error even if userknownhostsfile=/dev/null
            return await asyncssh.connect('192.168.2.249', username='melissali', client_keys=['/home/melissali/.ssh/id_rsa'], known_hosts=None, config=['/home/melissali/.ssh/config'])
        except OSError as e:
            print(f'Connection failed: {str(e)}')
        except asyncssh.Error as e:
            print(f'Connection failed: {str(e)}')
            asyncssh_logger.removeHandler(ch)
            # StringIO.getvalue() retrieves entire content of file
            log_content = log_string.getvalue()
            log_string.flush()
            print('Log content:')
            print(log_content)

    async def get_ssh_connection(self):
        if self.connection is None:
            self.connection = await self._remote_connection()
        return self.connection

    async def execute_command(self, cmd, stdin=None):
        conn = self.connection
        r = await conn.run(cmd, input=stdin.encode() if stdin else None)
        # print(r.stdout)
        out = r.stdout.rstrip('\n')
        err = r.stderr.rstrip('\n')
        print(f'out: {out}')
        print(f'err: {err}')
        print(f'code: {r.returncode}')
        return out, err, r.returncode

    def do_something(self):
        asyncio.get_event_loop().run_until_complete(self.get_ssh_connection())
        asyncio.get_event_loop().run_until_complete(self.execute_command('echo foo'))
        
    def do_something_else(self):
        asyncio.get_event_loop().run_until_complete(self.get_ssh_connection())
        asyncio.get_event_loop().run_until_complete(self.execute_command('echo melissa'))
        asyncio.get_event_loop().run_until_complete(self.execute_command('ls doesntexist'))

def main():
    a = SSHConnection()
    a.do_something()
    a.do_something_else()

    # logging shows that there are multiple SSH sessions in one connection
    asyncssh_logger.removeHandler(ch)
    # StringIO.getvalue() retrieves entire content of file
    log_content = log_string.getvalue()
    log_string.flush()
    print('Log content:')
    print(log_content)


if __name__ == '__main__':
    main()
