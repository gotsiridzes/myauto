from os import getenv


def bucket_arguments(parser):
    parser.add_argument(
        'name',
        type=str,
        help="Pass bucket name."
    )

    parser.add_argument(
        "-dmp",
        "--download_myauto_pictures",
        help="flag to download myauto's first page pictures.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )
    
    parser.add_argument(
        "-amp",
        "--archive_myauto_pictures",
        help="flag to archive downloaded photos.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )

    parser.add_argument(
        "-ump",
        "--upload_myauto_pictures",
        help="flag upload downloaded pictures.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )

    parser.add_argument(
        "-arp",
        "--assign_read_policy",
        help="flag to assign read bucket policy.",
        choices=["False", "True"],
        type=str,
        nargs="?",
        const="True",
        default="False"
    )

    parser.add_argument(
        "-lo",
        "--list_objects",
        type=str,
        help="list bucket object",
        nargs="?",
        const="True",
        default="False"
    )

    return parser
