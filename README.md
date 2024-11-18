The script is based on [FuncomDBFixGenerator
](https://github.com/VoidEssy/FuncomDBFixGenerator) thanks to the users from Admins United: Conan Discord.

===========================================================================
Basically the script to fix:
LogPackageName:Warning: String asset reference "None" is in short form, which is unsupported and -- even if valid -- resolving it will be really slow.
LogPackageName:Warning: Please consider resaving package in order to speed-up loading.

Script is looking for pattern  **Couldn't find file for package BP_ requested by async loading code. NameToLoad:**

![alt text](https://cdn.discordapp.com/attachments/1077995857108017344/1307897879813161001/image.png?ex=673bfa52&is=673aa8d2&hm=3275126fc46f2da90ba07f63793dab153ab804c22fe2382917a0d5259b4d156a&)
