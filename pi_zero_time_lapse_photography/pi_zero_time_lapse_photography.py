# -*- coding: utf-8 -*-

"""
Takes two pictures.
- One is saved to /var/www/index/ so you can view it in a browser at:
    http://<hostname>/web_image.png
- The other in saved locally, then can be SCPed to a remote mahine.

Notes:
- Install apache2:
    sudo apt install apache2
- Delete /var/www/index/index.html
- chmod 777 -R /var/www/index so you can write the web_image file to it. This is
not secure, obviously.
"""

from picamera import PiCamera
from time import sleep
import os
from datetime import datetime, date
import paramiko
from scp import SCPClient


def day_counter():
    """
    Set today's date in the start_date variable.
    """

    start_date = date(2019,11,7)
    today = date.today()

    return (today-start_date).days + 1


def current_date_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def take_a_picture(image_path):
    print("{} - Taking a picture".format(current_date_time()))
    camera.start_preview()
    camera.annotate_text = "Day {} {}".format(
        day_counter(),
        datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    sleep(2)
    camera.capture(image_path, format="png")
    print("{} - Picture taken {}".format(current_date_time(), image_path))

    return image_path


def ssh_image_to_recipient(image_path):
    hostname = "ENTER RECIPIENT MACHINE'S HOSTNAME HERE"
    username = "ENTER RECIPIENT MACHINE'S USERNAME HERE"
    password = "ENTER RECIPIENT MACHINE'S PASSWORD HERE"
    remote_path = "ENTER PATH ON RECIPIENT MACHINE WHERE FILE WILL BE SCPed TO"

    print("{} - Connecting to {}@{}".format(
        current_date_time(), username, hostname)
    )
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname,username=username,password=password)
        print("{} - Connection successful".format(current_date_time()))

        with SCPClient(ssh.get_transport()) as scp:
            print("{} - SCPing picture to {}@{} {}".format(
                current_date_time(),
                username,
                hostname,
                image_path)
            )
            try:
                scp.put(image_path, remote_path=remote_path)
                print("{} - SCPing complete {}".format(
                    current_date_time(),
                    os.path.join(remote_path,
                    os.path.basename(image_path)))
                )

                print("{} - Deleting {}".format(current_date_time(), image_path))
                os.remove(image_path)
            except Exception as e:
                print("{} - Error SCPing picture {} - {}".format(
                    current_date_time(), type(e), str(e))
                )


def main():
    take_a_picture(image_path=local_image_path)
    take_a_picture(image_path=web_image_path)
    ssh_image_to_recipient(image_path=local_image_path)

camera = PiCamera()
camera.resolution = (1280, 720)

if __name__ == "__main__":
    web_image_dir = "/var/www/html"
    web_image_path = os.path.join(web_image_dir, "web_image.png")

    local_image_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "time_lapse_images"
    )
    local_image_path = os.path.join(local_image_dir, "Day{}.{}.png".format(
        day_counter(),
        datetime.now().strftime("%Y-%m-%d.%H%M%S"))
    )

    if not os.path.isdir(local_image_dir):
        os.makedirs(local_image_dir)

    main()
