#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup as bs
import re
from github import Github
import base64
import sys

target = [
    "epoch-1-documentdownloader-links",
    "epoch-2-documentdownloader-links",
    "epoch-3-documentdownloader-links",
    "epoch-1-payloads-by-document-sha256---all-times-utc",
    "epoch-2-payloads-by-document-sha256---all-times-utc",
    "epoch-3-payloads-by-document-sha256---all-times-utc",
    "epoch-1-payload-urls-from-unknown-document",
    "epoch-2-payload-urls-from-unknown-document",
    "epoch-3-payload-urls-from-unknown-document",
    "epoch-1-c2s",
    "epoch-2-c2s",
    "epoch-3-c2s",
    "epoch-1---spam-c2s",
    "epoch-2---spam-c2s",
    "epoch-3---spam-c2s",
    "epoch-1---stealer-c2s",
    "epoch-2---stealer-c2s",
    "epoch-3---stealer-c2s",
    "loader-report"
    ]

token = "here_your_github_token"
g = Github(token)
repo = g.get_repo("netwitness999/feed")


def extract(code_block):
    code = code_block.find("code").text
    domain = [re.sub(r"^https?://([^/]+)(:\d+)?/.+", r"\1", line) for line in code.split("\n") if re.match(r"https?://.+", line)]
    ip = [re.sub(r":.+", "", line) for line in code.split("\n") if isIP(line)]
    domain.extend(ip)
    return domain


def isIP(token):
    return re.match(r"(\d{1,3}\.){3}\d{1,3}", token)


def update_to_github(filename, content, message):
    repo.update_file(filename, message, content, repo.get_contents(filename).sha)
    

def create_to_github(filename, content, message):
    repo.create_file(filename, message, content)
    

def get_from_github(filename):
    file = repo.get_contents(filename)
    return base64.b64decode(file.content).decode("utf-8").split("\n")

    
def get_origin():
    home = "https://paste.cryptolaemus.com/"
    soup = bs(requests.get(home).text, "html.parser")
    h4 = soup.find("h4")
    time = h4.find("time").text
    href = h4.find("a").attrs["href"]
    return time, href, requests.get(home + href).text


def get_IoC_list(origin):
    soup = bs(origin, "html.parser")
    code_list = soup.findAll("div", class_="highlighter-rouge")
    id_list = [tag.attrs["id"] for tag in soup.findAll(["h3", "h4"])]
    result = []
    for i in range(len(id_list)):
        if id_list[i] in target:
            result.extend(extract(code_list[i-1]))
    result = list(set(result))
    ip = [token for token in result if isIP(token)]
    domain = [token for token in result if not isIP(token)]
    return ip, domain


if __name__ == "__main__":

    time, href, origin = get_origin()
    filename = href.split("/")[-1].split(".")[0].split("_")
    ioc_domain = "emotet/%s-domain_%s" % (filename[0], filename[1])
    ioc_ip = "emotet/%s-ip_%s" % (filename[0], filename[1])

    # check exist file
    try:
        get_from_github(ioc_domain)
        get_from_github(ioc_ip)
        sys.exit()
    except Exception:
        pass

    # get IOC list
    ip, domain = get_IoC_list(origin)

    # create new list
    repo.create_file(ioc_domain, time, "\n".join(domain))
    repo.create_file(ioc_ip, time, "\n".join(ip))

    # update latest list
    update_to_github("emotet/latest_domain", "\n".join(domain), time)
    update_to_github("emotet/latest_ip", "\n".join(ip), time)

    # update composit list
    domain.extend(get_from_github("emotet/composit_domain"))
    domain = list(set(domain))
    if "" in domain:
        domain.remove("")
    ip.extend(get_from_github("emotet/composit_ip"))
    ip = list(set(ip))
    if "" in ip:
        ip.remove("")
    update_to_github("emotet/composit_domain", "\n".join(domain), time)
    update_to_github("emotet/composit_ip", "\n".join(ip), time)
