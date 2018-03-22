import os

from jupyterhub.spawner import LocalProcessSpawner

config = '/opt/app-root/src/.jupyter/jupyter_notebook_config.py'

class CustomLocalProcessSpawner(LocalProcessSpawner):

    cmd = [ 'jupyter-labhub' ]

    default_url = '/lab'

    args = [ '--config=%s' % config ]

    service = os.environ['JUPYTERHUB_SERVICE_NAME']

    profiles = [
        ('kg-1', 'Kernel Gateway #1', 'http://%s-kg-1:8080/' % service, 'colonels'),
        ('kg-2', 'Kernel Gateway #2', 'http://%s-kg-2:8080/' % service, 'colonels'),
        ('kg-3', 'Kernel Gateway #3', 'http://%s-kg-3:8080/' % service, 'colonels'),
    ]

    form_template = """
        <label for="profile">Select a profile:</label>
        <select class="form-control" name="profile" required autofocus>
        {input_template}
        </select>
        """

    input_template = """
        <option value="{key}" {first}>{display}</option>
        """

    def _options_form_default(self):
        temp_keys = [ dict(key=p[0], display=p[1], first='') for p in self.profiles ]
        temp_keys[0]['first'] = 'selected'
        text = ''.join([ self.input_template.format(**tk) for tk in temp_keys ])
        return self.form_template.format(input_template=text)

    def options_from_form(self, formdata):
        profile = formdata.get('profile', [None])[0]

        if not profile:
            raise RuntimeError('Profile has not been supplied.')

        options = {}

        for p in self.profiles:
            if p[0] == profile:
                options['profile'] = p
                break
        else:
            options['profile'] = self.profiles[0]

        return options

    def user_env(self, env):
        env['USER'] = 'default'
        env['HOME'] = '/opt/app-root/data/%s' % self.user.name
        env['SHELL'] = '/bin/bash'

        return env
    
    def get_env(self):
        env = super().get_env()

        env['LD_LIBRARY_PATH'] = os.environ['LD_LIBRARY_PATH']
        env['LD_PRELOAD'] = os.environ['LD_PRELOAD']
        env['NSS_WRAPPER_PASSWD'] = os.environ['NSS_WRAPPER_PASSWD']
        env['NSS_WRAPPER_GROUP'] = os.environ['NSS_WRAPPER_GROUP']
        env['PYTHONUNBUFFERED'] = os.environ['PYTHONUNBUFFERED']
        env['PYTHONIOENCODING'] = os.environ['PYTHONIOENCODING']

        profile = self.user_options['profile']

        env['KG_URL'] = profile[2]
        env['KG_AUTH_TOKEN'] = profile[3]

        return env

    def make_preexec_fn(self, name):
        def preexec():
            home = '/opt/app-root/data/%s' % name
            if not os.path.exists(home):
                os.mkdir(home)
            os.chdir(home)
        return preexec

c.JupyterHub.spawner_class = CustomLocalProcessSpawner
