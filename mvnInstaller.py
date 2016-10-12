import logging
import yaml

import os.path as path

try:
    from urllib import urlretrieve as url_retrieve
except:
    from urllib.request import urlretrieve as url_retrieve

from os import remove, chmod
from platform import platform
from subprocess import check_call
from zipfile import ZipFile


MVN_URL = 'https://archive.apache.org/dist/maven/maven-3/3.2.2/binaries/apache-maven-3.2.2-bin.zip'
MVN_ARGS = []

POM_URL = ''

is_system_mvn = False


def _read_config():
    global POM_URL, MVN_ARGS

    with open('mvnInstaller.yml', 'r') as config:
        yml_cfg = yaml.load(config)

        POM_URL = yml_cfg['pom']['url']
        MVN_ARGS = yml_cfg['mvn']['args']


def _check_maven():
    global is_system_mvn

    try:
        check_call(['mvn', '-h'])
        is_system_mvn = True
    except:
        logging.info("Maven isn't installed as a System util. Proceeding to download...")
        _install_maven()


def _install_maven():
    downloaded = path.exists("apache-maven-3.2.2")

    if not downloaded:
        logging.info("Downloading Maven from %s" % MVN_URL)
        try:
            url_retrieve(MVN_URL, "mvn.zip")
            downloaded = True
            logging.info("Download completed.")
        except:
            logging.error("Error downloading Maven")

        if downloaded:
            logging.info("Extracting downloaded Maven")
            try:
                with ZipFile('mvn.zip', 'r') as mvn_zip:
                    mvn_zip.extractall()

                logging.info("Cleaning up downloaded zip after successful extraction...")
                remove("mvn.zip")
            except:
                logging.error("Extraction failed")
    else:
        logging.info("Maven already downloaded.")


def _retrieve_pom():
    try:
        url_retrieve(POM_URL, 'pom.xml')
        logging.info("pom.xml download completed.")
    except Exception as e:
        logging.error("Error downloading pom.xml: %s" % e)


def _update_mvn_permissions(mvn_script):
    logging.info("Updating script permissions for %s" % mvn_script)
    chmod(mvn_script, 0o777)


def _get_mvn_path():
    mvn_path = "mvn"
    if not is_system_mvn:
        logging.debug("Preparing local Maven installation.")

        mvn_script = "mvn"
        if platform() == 'Windows':
            mvn_script += ".bat"

        mvn_path = path.join(path.curdir, "apache-maven-3.2.2", "bin", mvn_script)
        _update_mvn_permissions(mvn_path)

        logging.info("Maven found at %s" % mvn_path)
    else:
        logging.info("Maven found as System util")

    return mvn_path


def _execute_pom():
    downloaded = path.exists("pom.xml")

    if not downloaded:
        logging.error("Couldn't find pom.xml. Check log")
    else:
        logging.info("Executing pom.xml")

        mvn_cmd = _get_mvn_path()

        try:
            check_call([mvn_cmd] + MVN_ARGS)
            logging.info("pom.xml execution completed.")
        except:
            logging.error("Error during pom.xml execution")


def main():
    logging.basicConfig(filename='mvnInstaller.log', level=logging.INFO)
    logging.info("Reading configuration")
    _read_config()
    logging.info("Checking installed Maven")
    _check_maven()
    logging.info("Downloading pom.xml from %s" % POM_URL)
    _retrieve_pom()
    logging.info("Executing pom.xml")
    _execute_pom()

if __name__ == '__main__':
    main()