def unsetProxy(log=True):
    import subprocess
    proxies = subprocess.run("echo $HTTP_PROXY && echo $HTTPS_PROXY && echo $http_proxy && echo $https_proxy", capture_output=True, text=True)
    isProxy = False
    if proxies.stdout == "\n\n\n\n":
        if log:
            print("no proxies setted, good to go")
        pass
    else:
        subprocess.run("unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy") # no need to capture anything
