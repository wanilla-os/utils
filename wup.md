# usage of wup

`wup archive.tar.gz` - upack archive to this dir, change dir(cd) and start bash
after bash will be input name of package to add in installed.txt

`wup https://site.com/archive.tar.gz` - download archive to ~/.cache/wup/archives and unpack archive in ~/.cache/wup/sources 

`wup create` - interactive script maker for package/ First need to paste tar.gz download link, after links for additional components e.g. patches
after this name of package, version, after will be started bash. All comands in bash will be writed ti script file, be careful(exception - commands starts with space)!
after all comands need make ctrl + d, will be created bash script in `install_<pakagename>.sh`

`wup all` - print all installed packages in file installed.txt

`sudo python3 wup.py install` - install wup in system and create dirs

`wup add pkg-1.0` - add package to list of installed(if installed without wup)

`wup` - start interactive mode
