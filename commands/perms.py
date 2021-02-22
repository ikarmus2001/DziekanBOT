# async def perms(message,args):
# if (
#         command == "perms"
#         or command == "permissions"
#         and await self.checkPerms(message, "permissions")
#     ):
#         if (
#             args[0] == "set"
#             and len(args) == 3
#             and await self.checkPerms(message, "permissions_manage")
#         ):
#             try:
#                 lvl = int(args[2])
#                 if len(message.role_mentions) == 1:
#                     role_id = message.raw_role_mentions[0]
#                 else:
#                     role_id = args[1]
#             except:
#                 await message.reply(
#                     f"Please specify a permission level and role to assign the permission to."
#                 )
#             else:
#                 if lvl not in range(1, 3):
#                     await message.reply("Perms level can only be 1 or 2")
#                 else:
#                     if self.managePerms("set", level=lvl, role=role_id):
#                         await message.reply("Role permission changed successfully")
#                         if self.logsActive:
#                             await self.log(message)
#                     else:
#                         await message.reply(
#                             "Error occured while changing role permissions."
#                         )
#
#         elif (args[0] == "delete" or args[0] == "del") and await self.checkPerms(
#             message, "permissions_manage"
#         ):
#             if len(args) == 2:
#                 if len(message.role_mentions) == 1:
#                     role_id = message.raw_role_mentions[0]
#                 else:
#                     role_id = args[1]
#                 if self.managePerms("delete", role=role_id):
#                     if self.logsActive:
#                         await self.log(message)
#                     await message.reply("Role permission deleted successfully")
#                 else:
#                     await message.reply(
#                         "Error occured while deleting role permissions."
#                     )
#             else:
#                 await message.reply(
#                     f"Please specify a role to delete the permission from."
#                 )
#
#
#         elif not any(args):
#             perm_lvl = self.getUserPerms(message.author)
#             await message.reply(
#                 f"Your permission level: `{perm_lvl if perm_lvl < 3 else 'GOD'}`"
#             )
#
