###
# Copyright 2020 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
""" Delete Logical Drive Command for rdmc """

import sys

from argparse import ArgumentParser

from six.moves import input

from rdmc_base_classes import RdmcCommandBase, add_login_arguments_group, login_select_validation, \
                                logout_routine
from rdmc_helper import ReturnCodes, InvalidCommandLineError, Encryption, \
                    InvalidCommandLineErrorOPTS, NoContentsFoundForOperationError

class DeleteLogicalDriveCommand(RdmcCommandBase):
    """ Delete logical drive command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='deletelogicaldrive',\
            usage='deletelogicaldrive [OPTIONS]\n\n\tTo delete a logical ' \
                'drive a controller by index.\n\texample: deletelogicaldrive ' \
                '1 --controller=1\n\n\tTo delete multiple logical drives by ' \
                'index.\n\texample: deletelogicaldrive 1,2 --controller=1' \
                '\n\n\tTo delete all logical drives on a controller.\n\t' \
                'example: deletelogicaldrive --controller=1 --all\n\n\t'\
                'example: deletelogicaldrive --controller="Slot1" --all\n\n\tNOTE: ' \
                'You can also delete logical drives by ' \
                '"VolumeUniqueIdentifier".\n\n\t' \
                'You can also delete logical drives by ' \
                '"LogicalDriveName".', \
            summary='Deletes logical drives from the selected controller.',\
            aliases=['deletelogicaldrive'],\
            argparser=ArgumentParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.selobj = rdmcObj.commands_dict["SelectCommand"](rdmcObj)

    def run(self, line):
        """ Main disk inventory worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except (InvalidCommandLineErrorOPTS, SystemExit):
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")

        self.deletelogicaldrivevalidation(options)

        self.selobj.selectfunction("SmartStorageConfig.")
        content = self._rdmc.app.getprops()

        if not args and not options.all:
            raise InvalidCommandLineError('You must include a logical drive to delete.')
        elif not options.controller:
            raise InvalidCommandLineError('You must include a controller to select.')
        else:
            if len(args) > 1:
                logicaldrives = args
            elif len(args) == 1:
                logicaldrives = args[0].replace(', ', ',').split(',')
            else:
                logicaldrives = None

        controllist = []

        try:
            if options.controller.isdigit():
                if int(options.controller) > 0:
                    controllist.append(content[int(options.controller) - 1])
            else:
                slotcontrol = options.controller.lower().strip('\"').split('slot')[-1].lstrip()
                for control in content:
                    if slotcontrol.lower() == control["Location"].lower().split('slot')[-1].lstrip():
                        controllist.append(control)
            if not controllist:
                raise InvalidCommandLineError("")
        except InvalidCommandLineError:
            raise InvalidCommandLineError("Selected controller not found in the current inventory "\
                                          "list.")

        self.deletelogicaldrives(controllist, logicaldrives, options.all, options.force)

        logout_routine(self, options)
        #Return code
        return ReturnCodes.SUCCESS

    def deletelogicaldrives(self, controllist, drivelist, allopt, force):
        """Gets logical drives ready for deletion

        :param controllist: list of controllers
        :type controllist: list.
        :param drivelist: logical drives to delete
        :type drivelist: list.
        :param allopt: flag for deleting all logical drives
        :type allopt: bool.
        """

        for controller in controllist:
            changes = False

            numdrives = len(controller['LogicalDrives'])
            deletecount = 0

            if allopt:
                controller['LogicalDrives'] = []
                controller['DataGuard'] = "Disabled"
                self.lastlogicaldrive(controller)
                changes = True
            else:
                for deldrive in drivelist:
                    found = False

                    if deldrive.isdigit():
                        deldrive = int(deldrive)

                    for idx, ldrive in enumerate(controller['LogicalDrives']):
                        if deldrive == ldrive['VolumeUniqueIdentifier'] or deldrive == idx+1 or \
                        deldrive == ldrive['LogicalDriveName']:
                            if not force:
                                while True:
                                    ans = input("Are you sure you would"\
                                            " like to continue deleting drive"\
                                            ' %s? (y/n)' % ldrive['LogicalDriveName'])

                                    if ans.lower() == 'y':
                                        break
                                    elif ans.lower() == 'n':
                                        sys.stdout.write("Stopping command without "\
                                                "deleting logical drive.\n")
                                        return
                            sys.stdout.write('Setting logical drive %s ' \
                                             'for deletion\n' % ldrive['LogicalDriveName'])

                            controller['LogicalDrives'][idx]['Actions'] = \
                                        [{"Action": "LogicalDriveDelete"}]

                            controller['DataGuard'] = "Permissive"
                            deletecount += 1

                            changes = True
                            found = True
                            break

                    if not found:
                        raise NoContentsFoundForOperationError('Logical '\
                                        'drive %s not found.'% str(deldrive))

                if deletecount == numdrives:
                    self.lastlogicaldrive(controller)

            if changes:
                self._rdmc.app.put_handler(controller["@odata.id"], controller,\
                    headers={'If-Match': self.getetag(controller['@odata.id'])})
                self._rdmc.app.download_path([controller["@odata.id"]], path_refresh=True, \
                                                 crawl=False)

    def lastlogicaldrive(self, controller):
        """Special case that sets required properties after last drive deletion

        :param controller: controller change settings on
        :type controller: dict.
        """
        changelist = ['PredictiveSpareRebuild', 'SurfaceScanAnalysisPriority', \
                  'FlexibleLatencySchedulerSetting', 'DegradedPerformanceOptimization', \
                  'CurrentParallelSurfaceScanCount', 'SurfaceScanAnalysisDelaySeconds', \
                  'MonitorAndPerformanceAnalysisDelaySeconds', \
                  'InconsistencyRepairPolicy', 'DriveWriteCache', \
                  'ExpandPriority', 'EncryptionEULA', 'NoBatteryWriteCache', \
                  'ReadCachePercent', 'WriteCacheBypassThresholdKiB', \
                  'RebuildPriority', 'QueueDepth', 'ElevatorSort']

        for item in changelist:
            if item in list(controller.keys()):
                controller[item] = None

    def getetag(self, path):
        """ get etag from path """
        etag = None
        instance = self._rdmc.app.monolith.path(path)
        if instance:
            etag = instance.resp.getheader('etag') if 'etag' in instance.resp.getheaders() \
                                            else instance.resp.getheader('ETag')
        return etag

    def deletelogicaldrivevalidation(self, options):
        """ delete logical drive validation function

        :param options: command line options
        :type options: list.
        """
        login_select_validation(self, options)

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        add_login_arguments_group(customparser)

        customparser.add_argument(
            '--controller',
            dest='controller',
            help="""Use this flag to select the corresponding controller """ \
                """using either the slot number or index.""",
            default=None,
        )
        customparser.add_argument(
            '--all',
            dest='all',
            help="""Use this flag to delete all logical drives on a """ \
                """controller.""",
            action="store_true",
            default=False,
        )
        customparser.add_argument(
            '--force',
            dest='force',
            help="""Use this flag to override the "are you sure?" text when """ \
                """deleting a logical drive.""",
            action="store_true",
            default=False,
        )
