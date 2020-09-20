Summary
-------
The google_osconfig_agent process is a component GoogleCloudPlatform (https://github.com/GoogleCloudPlatform/osconfig) 
tooling, running on each VM by default. The agent is running as root and responsible for some user-controllable services, 
including OS config (https://cloud.google.com/compute/docs/os-config-management), which is kind of a poll based desired 
state configuration implementation of Google. 

This repo is hosting a demo about a privilege escalation flaw I identified in the implementation (and was fixed by 
Google since then).


Issue
-----
Tasks to be executed are called recipes, and one of the supported recipe types is executing a shell a script. 
While processing such a recipe, the agent - that is running as root with full capabilities - saves files temporarily in the 
/tmp directory, and then executes them. 
The directory created by the agent can be hijacked and thus the script to be executed can be replaced, 
effectively leading to local elevation of privileges.


Steps to reproduce
------------------

1. Preparing the environment:

```
        gcloud services enable osconfig.googleapis.com 
        gcloud compute project-info add-metadata --metadata=enable-osconfig=TRUE    
```

2. On the VM, running the exploit script as a low privileged user (nobody)

```
        # cat /tmp/poc.txt
        cat: /tmp/poc.txt: No such file or directory

        # pip3 install inotify_simple
        # chroot --userspec=nobody:nogroup / /home/radimre83/osconfig-privesc-poc3.py
        Running as 65534
        calling inotify.read()
        ...
```

3. Configuring an os-config policy:

```
        gcloud beta compute os-config guest-policies create test-policy-poc --file="C:\Projects\gcp-app-engine-experiments\compute-engine\osconfig-policy-poc.yaml"
```

4. Output of the poc script when the runscript is deployed (can be 10-15 minutes):

```
        Event(wd=1, mask=1073742080, cookie=0, name='recipe-runscript')
        New recipe: recipe-runscript2, rename: /tmp/osconfig_software_recipes.mali1596821311/xxx-recipe-name -> /tmp/osconfig_software_recipes.mali1596821311/recipe-runscript
        New rundir recipe-runscript2, rename: /tmp/osconfig_software_recipes.mali1596821311/recipe-runscript/xxx-rundir -> /tmp/osconfig_software_recipes.mali1596821311/recipe-runscript/run_1596821899000709826
```

5. Verify:

```
        # cat /tmp/poc.txt
        uid=0(root) gid=0(root) groups=0(root),1000(google-sudoers)
```


OS: f1-micro instance of GCE with the default Debian 10 image.


The fix
-------
Google turned to using random temp directory instead of a predictable one.


Remediation
------------
The fixed version was released 2020-09-05. You need to upgrade your OS package.




Attack scenario
---------------
This is a local privilege escalation vulnerability, so it could be exploited by someone who already has code execution 
rights on the affected GCE VMs:

- someone having low privileged shell

- an attacker via a network service already compromised

The key point is taking over the "base directory" (/tmp/osconfig_software_recipes) which is possible if no recipes 
have been processed in the current session yet, which means:

- no recipes have been executed at all so far (e.g. the osconfig feature was not in use, but will be at some point later)

- the VM is rebooted and all recipes are present in the db (/var/lib/google/osconfig_recipedb),  but some policy updates are executed at some point later

While this special combination indeed decreases the likelihood of exploitation, 
I think leveraging a work directory in /tmp is not secure here. (Neither did Google, this issue is fixed since.)


Timeline
--------
2020-08-07: Issue discovered and reported

2020-08-08: Issue triaged by Google, priority changed to P1

2020-08-10: Issue confirmed by Google ("🎉 Nice catch!"), priority changed to P2, severity to S2

2020-08-14: Update about the VRP process

2020-09-05: Issue fixed by Google



Credits
-------
Imre Rad


Links
-----
https://github.com/GoogleCloudPlatform/osconfig

https://issuetracker.google.com/issues/163147689

https://github.com/GoogleCloudPlatform/osconfig/commit/fa7e4ba5ee85be212ffbac66d96862c792bd270c

https://www.linkedin.com/in/imre-rad-2358749b/
