The script is based on [FuncomDBFixGenerator
](https://github.com/VoidEssy/FuncomDBFixGenerator) thanks to the users from Admins United: Conan Discord.

===========================================================================
Basically the script to fix:
<p>LogPackageName:Warning: String asset reference "None" is in short form, which is unsupported and -- even if valid -- resolving it will be really slow.</p>
<p>LogPackageName:Warning: Please consider resaving package in order to speed-up loading.</p>

Script is looking for pattern  **LogStreaming:Error: Couldn't find file for package (.*?) requested by async loading code.'**

![alt text](https://cdn.discordapp.com/attachments/1077995857108017344/1307897879813161001/image.png?ex=673bfa52&is=673aa8d2&hm=3275126fc46f2da90ba07f63793dab153ab804c22fe2382917a0d5259b4d156a&)

Why this is happening ?
Seems to have started after Funcoms barkeeper hotfix.

In short **Some leftover placable actors remained in the world - after they have been removed or renamed in the mod by the mod author, or mod was removed from the server but placable actor was placed by a user prior.

In theory server should clean this actors up or skip the search, but seems to be stuck on SearchForPackageOnDisk.
