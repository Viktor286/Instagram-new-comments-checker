# -*- coding: utf-8 -*-

# This is Instagram "new comments checker" v1.1
# It keeps records of all new comments left by others for a particular user (no authentication needed).
# It sends "new comments" report to email by Google mail service (authentication needed).
# The classic Instagram interface doesn't show all the new comments explicitly, especially if there are a lot of notifications.

# The script works like program service, it's launching new "comments checkup" sessions 4 times per 24 hours.
# During the work, the script will display all action's descriptions in the log.

# Uses MySQL database, 2 tables: comments, media. Tables structure described below.

# Functionality description
# Script waits for a scheduled time after launch to perform new comments checkup session.
# When time will come, it parses posts(media) comments chains, saves the states of these in DB.
# After each new comments session will send a report with new comments to email (in case new comments exists).

# To allow Gmail service send mail, you should add this ability to Authorised Apps list in Google settings.
# https://www.google.com/settings/security/lesssecureapps
# https://security.google.com/settings/security/apppasswords

# -------- Configuration

username = "insta_user"  # Instagram username
target_email_address = "mail@mail.com"  # The recipient mail box
mail_title_string = " New Instagram comments for User Name "  # Title of the mail with report

# Google mail service authentication

gmail_address = "hel.mail.robot@gmail.com"
gmail_address_password = 'hwb5437he4g'

# Sessions schedule for "new comments check"
alarm_00 = a0 = "10:00:00"
alarm_01 = a1 = "15:00:00"
alarm_02 = a2 = "19:00:00"
alarm_03 = a3 = "11:30:00"

# Database connection config
db_cfg = {'host': 'localhost',  # host address
          'port': 3306,
          'database': 'db_name',  # the name of yor database schema.
          'user': 'db_user',  # your database's username
          'password': 'db_user_pass'  # your username's password
          }

# MySQL tables structures (create these in you custom database schema).

# CREATE TABLE `comments` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `id_comment` varchar(32) NOT NULL,
#   `linked_media_id` varchar(32) NOT NULL,
#   `linked_media_code` varchar(32) DEFAULT NULL,
#   `cmt_user_name` varchar(32) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `cmt_user_pic` varchar(152) DEFAULT NULL,
#   `cmt_user_id` varchar(32) DEFAULT NULL,
#   `text_comment` varchar(64) DEFAULT NULL,
#   PRIMARY KEY (`id`,`id_comment`,`linked_media_id`),
#   UNIQUE KEY `id_UNIQUE` (`id`),
#   UNIQUE KEY `id_comment_UNIQUE` (`id_comment`)
# ) ENGINE=MyISAM AUTO_INCREMENT DEFAULT CHARSET=utf8;


# CREATE TABLE `media` (
#   `id` int(11) NOT NULL AUTO_INCREMENT,
#   `post_id` varchar(32) NOT NULL,
#   `post_code` varchar(32) NOT NULL,
#   `post_comments_count` int(9) DEFAULT NULL,
#   `post_date` datetime DEFAULT NULL,
#   `post_likes` int(9) DEFAULT NULL,
#   `post_thumb` varchar(152) DEFAULT NULL,
#   `post_caption` varchar(152) DEFAULT NULL,
#   PRIMARY KEY (`id`,`post_id`,`post_code`),
#   UNIQUE KEY `id_UNIQUE` (`id`),
#   UNIQUE KEY `post_id_UNIQUE` (`post_id`),
#   UNIQUE KEY `post_code_UNIQUE` (`post_code`)
# ) ENGINE=MyISAM AUTO_INCREMENT DEFAULT CHARSET=utf8;


import requests
import time
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mysql.connector import MySQLConnection, Error

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
url_user_detail = 'https://www.instagram.com/%s/?__a=1'
url_user_detail_next_page = 'https://www.instagram.com/%s/?__a=1&max_id=%s'
url_media_detail = 'https://www.instagram.com/p/%s/?__a=1'
username_last_media = 'https://www.instagram.com/%s/media/'
media_link = 'https://www.instagram.com/p/%s/'

request_delay_media = 0
request_delay_comments = 0


def mysql_query(query):
    conn, cursor = '', ''
    try:
        conn = MySQLConnection(**db_cfg)
        cursor = conn.cursor()
        cursor.execute(query)
        # print(cursor.lastrowid)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def mysql_fetchall(query):
    conn, cursor = '', ''
    try:
        conn = MySQLConnection(**db_cfg)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        # print('Total Row(s):', cursor.rowcount)
        return rows
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def parse_page(has_next_page=True, cursor=''):

    if has_next_page is True:
        user_url = url_user_detail_next_page % (username, cursor)

        r = requests.get(user_url)
        page_data = r.json()

        posts = page_data['user']['media']['nodes']
        cursor = page_data['user']['media']['page_info']['end_cursor']
        has_next_page = page_data['user']['media']['page_info']['has_next_page']

        print('\n ---------- Transfer new parsed json data...')
        return {'posts': posts, 'info': [has_next_page, cursor]}

    else:
        print('\nThere is no more pages.')
        return False


def smart_truncate(content, length=90, suffix='...'):
    if len(content) <= length:
        return content
    else:
        # return ' '.join(content[:length + 1].split(' ')[0:-1]) + suffix
        return content[:length].rsplit(' ', 1)[0] + suffix


def send_gmail(receiver, subject, text, html):
    me = gmail_address
    you = receiver

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = you

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    try:
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        # https://www.google.com/settings/security/lesssecureapps
        # https://security.google.com/settings/security/apppasswords
        server_ssl.login(gmail_address, gmail_address_password)
        server_ssl.sendmail(me, you, msg.as_string())
        server_ssl.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")


# ------- Service starts ------- >

print("\nInstagram comments checker launched and waiting for scheduled time... \n" + a0 + "\n" + a1 + "\n" + a2 + "\n" + a3)
print("\n---> still waiting...")

while True:
    now_time = datetime.datetime.now()
    tm = now_time.strftime("%H:%M:%S")

    if tm == a0 or tm == a1 or tm == a2 or tm == a3:  # if True:  # debug fast start commented option
        print("! Instagram comments checker starts new check session at " + tm + " --->")
        list_of_user_media = []
        list_of_updated_media = []
        report = []
        page = [True, '']

        # 1. Check data about posts in remote site an local db
        # Request user page json
        user_url = url_user_detail % username
        r = requests.get(user_url)
        page_data = r.json()
        media_count = int(page_data['user']['media']['count'])

        # Get media count info from database
        check_cmnt_count_query = "SELECT count(*) FROM {database}.media".format(database=db_cfg['database'])

        db_media_count = mysql_fetchall(check_cmnt_count_query)

        # Set is_new_media flag
        is_new_media = 0 if media_count == int(db_media_count[0]['count(*)']) else 1

        # Show state
        media_count_compare = "No new media" if is_new_media is 0 else "Media updates available!"
        print("Total posts of %s is %s. (%s)" % (username, media_count, media_count_compare))
        print("Estimated time for parsing all posts is", request_delay_media * media_count / 12, "seconds, with delay",
              request_delay_media, "sec.")

        # post counter
        p = 0

        # 2. Check if new posts appears, to add new one to database
        # Collect existing online post for deleting these in database
        checked_posts_ids_in_this_session = []

        while page[0] is True:
            output = parse_page(page[0], page[1])
            print("Watching new %s page" % username)
            info = output['info']
            posts_dict = output['posts']

            has_next_page = info[0]
            cursor = info[1]

            # print(posts_dict)
            for post in posts_dict:
                # post counter outside the while loop
                p += 1
                # print("^^^ Start post loop %s ^^^" % p)

                post_ordinal_num = media_count - p

                post_link = media_link % post['code']
                post_code = post['code']
                post_likes = post['likes']['count']
                post_caption = post['caption'].replace('"', '')
                post_thumb = post['thumbnail_src']
                post_id = post['id']
                post_comments_count = post['comments']['count']
                post_date = post['date']
                post_date_sql = datetime.datetime.fromtimestamp(int(post['date'])).strftime('%Y-%m-%d %H:%M:%S')

                checked_posts_ids_in_this_session.append(int(post_id))  # collect online post list for database-up-to-date check

                # compare id and comments counts of medias from db and remote
                check_media_id_query = "SELECT post_comments_count FROM {database}.media WHERE post_id = '{post_id}'".\
                    format(post_id=post_id, database=db_cfg['database'])

                # print("------- Making SELECT post_id CHECK", post_id)
                db_media_row = mysql_fetchall(check_media_id_query)
                # print("------- Response: db_media_row", db_media_row)
                print("\nChecking post", post_ordinal_num)

                if len(db_media_row) >= 1:  # if len(db_media_row) > 0:
                    # print("This post №%s in db, moving on" % post_ordinal_num)
                    considered_count_of_comments_in_db = db_media_row[0]['post_comments_count']
                else:
                    # Media doesn't exist in db, THIS MEDIA IS NEW FOR DB
                    insert_media_query = ('INSERT INTO {database}.media(`id`, `post_id`, `post_code`, '
                                          '`post_comments_count`, `post_date`, `post_likes`, `post_thumb`, '
                                          '`post_caption`) VALUES ("", "{post_id}", "{post_code}", '
                                          '"{post_comments_count}", "{post_date}", "{post_likes}", "{post_thumb}", '
                                          '"{post_caption}")').format(
                        post_id=post_id, post_code=post_code, post_comments_count=post_comments_count,
                        post_date=post_date_sql, post_likes=post_likes, post_thumb=post_thumb, post_caption=post_caption,
                        database=db_cfg['database'])

                    print("Made record to database for this media --> ", post_link) if mysql_query(
                        insert_media_query) > 0 \
                        else print("Couldn't insert media to database", post_link)

                    # Reset considered comments number to zero, since the media is new for farther comparision
                    considered_count_of_comments_in_db = 0
                    # print("Set comments count to zero! Next will be ! New comments...")

                # print("Begin compare comments count...", int(considered_count_of_comments_in_db), int(post_comments_count))
                # New or existing media in database, ANYWAY compare db and online numbers of comments
                if int(considered_count_of_comments_in_db) == int(post_comments_count):
                    # Same number of comments in db, nothing to do here
                    print("This post №%s has no new comments: %s" % (post_ordinal_num, post_link))
                else:
                    # New Comments detected!
                    print("! Parsing new comments in this post №%s: %s" % (post_ordinal_num, post_link))

                    # Request media json page with comments
                    user_url = url_media_detail % post_code
                    r = requests.get(user_url)
                    page_data = r.json()

                    # Set media vars
                    linked_media_id = post_id
                    linked_media_code = post_code
                    post_link = media_link % linked_media_code
                    # comments_count = page_data['media']['comments']['count']
                    comments_count = page_data['graphql']['shortcode_media']['edge_media_to_comment']['count']
                    # comments = page_data['media']['comments']['nodes']
                    comments = page_data['graphql']['shortcode_media']['edge_media_to_comment']['edges']
                    print('** Total are %s comments' % comments_count)

                    # Cycle comments to compare online and db entries
                    print("** Looking into comments of this post...")
                    for comment in comments:
                        comment = comment['node']
                        created_at = comment['created_at']
                        created_at_sql = datetime.datetime.fromtimestamp(int(created_at)).strftime(
                            '%Y-%m-%d %H:%M:%S')
                        text_comment = comment['text'].replace('"', '')
                        id_comment = comment['id']
                        cmt_user_name = comment['owner']['username']
                        cmt_user_pic = comment['owner']['profile_pic_url']
                        cmt_user_id = comment['owner']['id']

                        check_comment_query = "SELECT id_comment FROM {database}.comments WHERE id_comment = " \
                                              "'{id_comment}'".format(id_comment=id_comment, database=db_cfg['database'])

                        db_comment_row = mysql_fetchall(check_comment_query)
                        if len(db_comment_row) > 0:
                            # This comments already in database
                            print("** Comment exist, skip it")
                        else:
                            # Insert new comment in db
                            print("** Comment is new, adding to database...")

                            insert_comments_query = '''INSERT INTO
                            {database}.comments(`id`, `id_comment`, `linked_media_id`, `linked_media_code`,
                            `cmt_user_name`, `created_at`, `cmt_user_pic`, `cmt_user_id`, `text_comment`)
                            VALUES ("", "{id_comment}", "{linked_media_id}", "{linked_media_code}", "{cmt_user_name}",
                            "{created_at}", "{cmt_user_pic}", "{cmt_user_id}", "{text_comment}")
                            '''.format(id_comment=id_comment, linked_media_id=linked_media_id,
                                       linked_media_code=linked_media_code, cmt_user_name=cmt_user_name,
                                       created_at=created_at_sql, cmt_user_pic=cmt_user_pic, cmt_user_id=cmt_user_id,
                                       text_comment=text_comment, database=db_cfg['database'])

                            print("** Insert new comment", id_comment, "for post", post_ordinal_num, "--> ", post_link) \
                                if mysql_query(insert_comments_query) > 0 else print(
                                "** Couldn't insert comment to database", post_link)

                            # Add new comment to report
                            report_array = {'id_comment': id_comment, 'linked_media_id': linked_media_id,
                                            'linked_media_code': linked_media_code, 'cmt_user_name': cmt_user_name,
                                            'created_at': created_at, 'cmt_user_pic': cmt_user_pic,
                                            'cmt_user_id': cmt_user_id, 'text_comment': text_comment,
                                            'post_thumb': post_thumb, 'post_caption': post_caption,
                                            'post_comments_count': post_comments_count}
                            report.append(report_array)
                            print("Added new report line:", report_array)

                        # A little delay for each comment
                        time.sleep(request_delay_comments)

                    # Update media in db
                    update_query = ("""
                    UPDATE {database}.media
                    SET post_comments_count = '{post_comments_count}', post_likes = '{post_likes}'
                    WHERE post_id = '{post_id}'
                    """).format(post_id=post_id, post_comments_count=post_comments_count,
                                post_likes=post_likes, database=db_cfg['database'])

                    print("--> Update comments count to database for this post №%s", post_ordinal_num, "-->", post_link) \
                        if mysql_query(update_query) == 0 else print("Couldn't update media in database!", post_link)

            # -- Post cycle ends
            # pagination driver

            page = [has_next_page, cursor]
            time.sleep(request_delay_media)

        report_items = len(report)
        html_mail_report_lines = ''
        text_lines = ''
        users_skip = 0

        now_time = datetime.datetime.now()
        complete_date = now_time.strftime("%d.%m")
        complete_time = now_time.strftime("%H:%M")

        # Check if the number of posts on local DB and on remote server is different
        # Ask local db for total number of media
        get_db_posts_total_count_query = "SELECT post_id FROM {database}.media".format(database=db_cfg['database'])
        get_db_posts_total_count = mysql_fetchall(get_db_posts_total_count_query)

        get_db_posts_total_count_list = []
        for d in get_db_posts_total_count:
            get_db_posts_total_count_list.append(int(d['post_id']))

        if len(get_db_posts_total_count_list) > media_count:
            posts_for_deletion = set(get_db_posts_total_count_list) - set(checked_posts_ids_in_this_session)

            if len(posts_for_deletion) > 0:
                print('\nSeems like ' + str(len(posts_for_deletion)) + ' post was deleted by user on remote host. '
                                                                       'Let\'s delete these from database too:\n')
                print(posts_for_deletion)  # Show preview set of deletable posts

                # Check if there are a lot of media for deletion
                input_confirmation = ''

                # Some additional checks
                if len(posts_for_deletion) > 5:
                    # If there are more then 5 posts for deletion we need to get approve for this from user.
                    input_confirmation = input("\nDo you want to DELETE all these from local database? Y/N\n")
                else:
                    # other way it seems like healthy behavior
                    input_confirmation = 'y'  # just set 'Yes' instead of user

                # Deletion process
                if input_confirmation.lower() == 'y' or input_confirmation.lower() == 'yes':
                    print("Performing deletion...")

                    for p in posts_for_deletion:
                        remote_media_public_state = True
                        # TODO: It will be great to check if media is really deleted otherwise we could keep deleting worked stuff

                        if remote_media_public_state:
                            print('-- Delete ' + str(p) + ' --')
                            post_for_deletion_query = "DELETE FROM {database}.comments WHERE linked_media_id='{linked_media_id}' "\
                                .format(database=db_cfg['database'], linked_media_id=p)

                            comments_for_deletion_query = "DELETE FROM {database}.media WHERE post_id='{post_id}' " \
                                .format(database=db_cfg['database'], post_id=p)

                            deleted_post = mysql_query(post_for_deletion_query)
                            deleted_comments = mysql_query(comments_for_deletion_query)
                else:
                    print("Just moving along.")
        else:
            print('\nLocal database media count corresponds remote number of media.')

        # -- End of Check media database state for delete missing ones

        print("\nReport contains " + str(report_items) + " posts")

        if report_items > 0:

            for r in report:

                # Skip user's comments
                if r['cmt_user_name'] == username:
                    users_skip += 1
                    continue

                created_time = datetime.datetime.fromtimestamp(int(r['created_at'])).strftime('%H:%M')
                created_date = datetime.datetime.fromtimestamp(int(r['created_at'])).strftime('%Y-%m-%d')
                post_caption = smart_truncate(r['post_caption'])

                html_mail_report_line = """

                <!-- report start-->
                <div class="report" style="font-family: 'Lato', Calibri, Arial, sans-serif; margin: 0 auto 20px; border: 1px solid #d6d6d6; padding: 0 20px 15px; width: 500px; min-width: 550px;">
                    <div class="line_01" style="clear: both; margin-bottom: 5px;  padding: 10px 0px 0px 0;">
                        <a href="https://www.instagram.com/p/{linked_media_code}/" target="_blank"><img src="{post_thumb}" alt="" width="75px" height="75px" class="post_thumb" style="position: relative; float: right; margin: 0 0 0 10px;"></a>
                        <div class="caption" style="font-size: 13px; color: #9BA6B0; width: 500px; margin-top: 6px;">{post_caption}</div>
                        <div class="total_comments" style="font-size: 11px; color: #9BA6B0; font-style: italic; padding-top: 5px; ">Total comments on post: <span style="color: #555555; font-weight: bold; font-style: normal; font-size: 13px;">{post_comments_count}</span></div>
                        <br style="clear: both;">
                    </div>

                    <div class="line_02" style="background-color: #fffbf0; min-height: 85px;">
                        <a href="https://www.instagram.com/{cmt_user_name}/" target="_blank"><img src="{cmt_user_pic}" width="75px" height="75px" alt="" class="userpic" style="position: relative; float: left; margin: 5px 10px 5px 5px;"></a>
                        <div class="date" style="font-size: 13px; color: #c5bbb4; margin: 5px 10px 0 0;  float: right; text-align: right;">{created_time}</div><div class="username" style="font-weight: bold; font-size: 18px; color: #554a42; padding-top: 2px; ">{cmt_user_name}</div>
                        <div class="comment" style="padding: 7px 15px 0; overflow: hidden;"><a href="https://www.instagram.com/p/{linked_media_code}/" target="_blank" style="color: #554a42 !important; text-decoration: none !important;; display: block !important;">{text_comment}</a></div>
                        <br style="clear: both;">
                    </div>
                </div>
                <!-- report end -->

                """.format(created_time=created_time,
                           created_date=created_date,
                           id_comment=r['id_comment'],
                           linked_media_id=r['linked_media_id'],
                           linked_media_code=r['linked_media_code'],
                           cmt_user_name=r['cmt_user_name'],
                           cmt_user_pic=r['cmt_user_pic'],
                           cmt_user_id=r['cmt_user_id'],
                           text_comment=r['text_comment'],
                           post_thumb=r['post_thumb'],
                           post_caption=post_caption,
                           post_comments_count=r['post_comments_count'])
                html_mail_report_lines += html_mail_report_line

                text_line = """Post https://www.instagram.com/p/{linked_media_code}
                Comment: {post_comments_count}
                {post_caption}

                {cmt_user_name}
                Post:
                {text_comment}
                at {created_time}

                """.format(created_time=created_time,
                           linked_media_code=r['linked_media_code'],
                           cmt_user_name=r['cmt_user_name'],
                           text_comment=r['text_comment'],
                           post_caption=post_caption,
                           post_comments_count=r['post_comments_count'])
                text_lines += text_line

            relevant_items_count = report_items - users_skip
            print("Relevant posts: " + str(relevant_items_count))

            if relevant_items_count > 0:

                text_header = mail_title_string + """
                Today's new: {relevant_items_count}
                Last update {complete_time}.
                """.format(report_items=report_items, complete_date=complete_date, complete_time=complete_time,
                           relevant_items_count=relevant_items_count)

                html_mail_top = """
                <!DOCTYPE html>
                <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                    <title>{mail_title_string}</title>
                </head>
                <body style="font-family: 'Lato', Calibri, Arial, sans-serif;">
                """

                html_mail_report_header = """
                <div style="font-family: 'Lato', Calibri, Arial, sans-serif; font-size: 14px; margin: 40px auto 3px; color: #8b725b; text-align: center; font-weight: normal; width: 500px; min-width: 550px;">Today's new: {relevant_items_count}. <br /> Last update {complete_time}. </div>
                <div style="font-family: 'Lato', Calibri, Arial, sans-serif; font-size: 24px; margin: 3px auto 5px; color: #8b725b; text-align: center; font-weight: normal; width: 500px; min-width: 550px;">{complete_date} {mail_title_string}: </div>
                <br style="clear: both;">
                """.format(report_items=report_items, complete_date=complete_date, complete_time=complete_time,
                           relevant_items_count=relevant_items_count, mail_title_string=mail_title_string)

                html_mail_bottom = """
                <div class="footer" style="height: 100px">&nbsp;</div>
                </body>
                </html>
                """

                html = html_mail_top + html_mail_report_header + html_mail_report_lines + html_mail_bottom
                text = text_header + text_lines

                print("Trying to send letter at %s %s..." % (complete_time, complete_date))
                send_gmail(target_email_address, complete_date + mail_title_string, text, html)

                print("\n-------------------------------------------------- "
                      "\nInstagram comments checker launched and waiting "
                      "for scheduled time... \n" + a0 + "\n" + a1 + "\n" + a2 + "\n" + a3)

                print("\n---> still waiting...\n\n\n")
            else:
                print("There is no updates from other users.")
        else:
            #  Empty Letter send mail here
            print("There is no updates this time")

    time.sleep(1)
