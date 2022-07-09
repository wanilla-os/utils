#!/usr/bin/python3
import os
import sys
import re
import subprocess
try:
    from prompt_toolkit import prompt
    import requests
    from alive_progress import alive_bar

    def download(url):
        archive_name = url.split('/', -1)[-1]
        run("mkdir -p "+os.environ['HOME']+"/.cache/wup/archives")

        with requests.get(url, stream=True) as r:
            lenght = int(r.headers.get('Content-Length', 1024))
            if lenght == 1024:
                lenght = len(r.content)
            print(f'need to get {lenght} bytes of data')
            with alive_bar(lenght, spinner_length=5, title="download "+archive_name) as bar:
                with open(os.environ['HOME']+"/.cache/wup/archives/"+archive_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                        bar(len(chunk))
        return os.environ['HOME']+"/.cache/wup/archives/"+archive_name

except:
    try:
        print('deps not found. Not full mode')
        import readline

        def prompt(msg, default=''):
            readline.set_startup_hook(lambda: readline.insert_text(default))
            try:
                return input(msg)  # or raw_input in Python 2
            finally:
                readline.set_startup_hook()

        def download(link):
            archive_name = link.split('/', -1)[-1]
            run("mkdir -p "+os.environ['HOME']+"/.cache/wup/archives")
            with open(os.environ['HOME']+"/.cache/wup/archives/"+archive_name, 'wb') as load_file:
                load_file.write(requests.get(link).content)
            return os.environ['HOME']+"/.cache/wup/archives/"+archive_name

    except:
        def prompt(msg, default=''):
            d = input(msg+"("+default+") ")
            if len(d) == 0:
                return default
            return d


def wget(url, directory=""):
    if directory:
        run("mkdir -p "+directory)
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        lenght = int(r.headers.get('Content-Length', 1024))
        if lenght == 1024:
            lenght = len(r.content)
        print(f'need to get {lenght} bytes of data')
        with open(directory + local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
    return directory + local_filename


def create():
    wget_list = []
    main_archive = prompt('link to tar gz or zip file> ')

    while True:
        l = prompt("additional download link e.g. patches (blank for cansel)> ")
        if l.strip() == "":
            break
        wget_list.append(l)

    pkg_name = prompt("package name> ")
    pkg_ver = prompt("package version> ")

    with open('install_'+pkg_name+".sh", 'w') as script:

        script.write("# install script for "+pkg_name+"-"+pkg_ver+"\n")

        now = run("pwd")[:-1]
        os.system('echo "# start commands for install" > ' +
                  now+"/"+pkg_name+".history")
        os.environ['HISTFILE'] = now+"/"+pkg_name+".history"

        ext = main_archive.split('/', -1)[-1].split('.', 1)[1]
        print(ext)

        script.write('mkdir '+pkg_name+"_install\n")
        os.system('mkdir '+pkg_name+"_install")
        script.write('cd '+pkg_name+"_install\n")
        os.chdir(pkg_name+"_install")

        os.system('wget --no-check-certificate ' +
                  main_archive+" -O "+pkg_name+'.'+ext)
        script.write('wget --no-check-certificate ' +
                     main_archive+" -O "+pkg_name+'.'+ext+"\n")

        for i in wget_list:
            wget(i)
            script.write('wget --no-check-certificate '+i+"\n")

        "pwd == ./neofeth_install"
        if str(main_archive).endswith('.zip'):

            os.system('unzip ' + pkg_name+'.'+ext)
            script.write('unzip ' + pkg_name+'.'+ext+"\n")
        else:
            files = run("tar -xpvf " + pkg_name+'.'+ext).split('\n', -1)[:-1]
            folder = files[0].split('/', -1)[0]
            many = False
            for f in files:
                if not str(f).startswith(folder):
                    many = True
                    break
            script.write("tar -xpf " + pkg_name+'.'+ext+"\n")

            if not many:
                os.chdir(folder)
                script.write("cd " + folder+"\n")

        os.system("PS1='" + pkg_name + " # ' bash --norc")

        sripts = run("cat " + os.environ['HISTFILE'])
        reg = r'cat (>+) (.*) << \"EOF\"'
        rs = re.findall(reg, sripts)
        for r in rs:
            spl = sripts.split("cat "+r[0], 1)
            print(len(spl))
            pre = spl[0]
            spl2 = spl[1].split('\n', 1)[1].split("EOF", 1)
            text = spl2[0]
            post = spl2[1]
            sripts = pre + '\n' + 'echo "' + \
                text.replace('"', r'\"') + '" '+r[0]+r[1]+' \n'+post
        script.write(sripts+"\n")
        os.system("echo "+pkg_name+"-"+pkg_ver+" >> /var/wup/installed.txt")


def run(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True,
                            stderr=subprocess.PIPE, universal_newlines=True)
    return result.stdout  # Отправка только вывода


def install():
    print(os.system("cp " + __file__+" /usr/bin/wup"))
    print(os.system("chmod +x /usr/bin/wup"))
    print(os.system("mkdir -p "+os.environ['HOME']+"/.cache/wup/archives"))
    print(os.system("mkdir -p "+os.environ['HOME']+"/.cache/wup/sources"))
    print(os.system("touch /var/wup/installed.txt"))
    print(os.system("chmod 666 /var/wup/installed.txt"))


def untar(pkg, pname=""):
    if pname == "":
        pname = pkg.split('/', -1)[-1][:-4]
    print(pkg)
    directory = ""
    if str(pkg).endswith('.zip'):
        os.system("mkdir -p "+pname)
        run("rm -rf "+pname)
        os.system('unzip ' + pkg + ' -d '+pname)
        directory = pname
    else:
        f = run(f"tar -tf "+pkg).split("\n")[:-1]
        directory = f[0].split('/', -1)[0]
        many = False
        for i in f:
            if not i.startswith(directory):
                print(i)
                many = True
                break
        if many:
            os.system("mkdir -p "+directory)
            os.system("tar -xpf "+pkg + " -C "+directory)
        else:
            os.system("tar -xpf "+pkg)
    os.system("cd "+directory+" && PS1='" + directory + " # ' bash --norc")
    d = prompt("pkg name > ", default=directory)
    print(d)
    if d in all():
        print('\n\nalready installed\n\n\n')
        return
    run("echo "+d+" >> /var/wup/installed.txt")


def dopkg(arg: str):
    if arg.startswith('http://') or arg.startswith('https://') or arg.startswith('ftp://'):
        if arg.endswith('html'):
            ...
        else:
            untar(download(arg))
    else:
        untar(arg)


def all():
    return run("cat /var/wup/installed.txt").split('\n')


def main(args):
    if len(args) == 1:
        while True:
            main(['wup', prompt('wup > ')])
    elif args[1] == "all":
        print("\n".join(all()))
    elif args[1] == "add":
        if args[2] in all():
            print('\n\nalready installed\n\n\n')
            return
        run("echo "+args[2]+" >> /var/wup/installed.txt")
    elif args[1] == "install":
        install()
    elif args[1] == "create":
        create()
    else:
        dopkg(args[1])


if __name__ == "__main__":
    main(sys.argv)
