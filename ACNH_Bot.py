# Work with Python 3.6
import discord
import asyncio
import random
import string
from collections import deque
from discord.ext import commands, tasks

#TOKEN for ACNH
TOKEN = ''
client = commands.Bot(command_prefix = "$")

client.list_enchere = []
client.list_status = False
client.vendeur_actuel = None
client.blackList = ['bmp','jpeg','jpg','png','gif','txt','xlsx','svg','com','fr']
client.message_spam = ""
client.counter = 0

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

##################### DELETING MESSAGES EVENT FUNCTION ###################

@client.event
async def on_message_edit(before,after):
    auth_perm = before.author.permissions_in(before.channel)
    data = iter(auth_perm)
    for item in data:
        if item == ('manage_messages',True):
            await client.process_commands(before)
            return

    if client.vendeur_actuel != None and before.author.id == client.vendeur_actuel.id:
        await client.process_commands(before)
        return

    await before.delete()
    message = await before.channel.send("Merci de ne pas éditer son message.")
    await asyncio.sleep(3)
    await message.delete()
    await client.process_commands(before)

@client.event
async def on_message(message):
    #id discord ACNH
    channel = client.get_channel()
    if message.channel == channel:
        auth_perm = message.author.permissions_in(message.channel)
        data = iter(auth_perm)

        if client.vendeur_actuel != None and message.author.id == client.vendeur_actuel.id:
                await client.process_commands(message)
                return

        if client.vendeur_actuel != None:
            if message.author.id != client.vendeur_actuel.id and "http" in message.content.lower():
                await message.delete()
                message_link = await message.channel.send("Merci de ne pas mettre de liens")
                await asyncio.sleep(3)
                await message_link.delete()
                await client.process_commands(message)
                return

        for item in data:
            if item == ('manage_messages',True):
                await client.process_commands(message)
                return
            if item == ('manage_messages',False):
                if len(message.content) >= 6:
                    #check if contain number if not delete
                    #if any(i.isdigit() for i in message.content) == False:
                    await message.delete()
                    message_com = await message.channel.send("Merci de ne pas faire de commentaires")
                    await asyncio.sleep(3)
                    await message_com.delete()
                    await client.process_commands(message)
                    return

                for attachment in message.attachments:
                    if attachment.filename.split('.')[-1] in client.blackList:
                        await message.delete()
                        await client.process_commands(message)
                        return

                if "http" in message.content.lower():
                    await message.delete()
                    message_link = await message.channel.send("Merci de ne pas mettre de liens")
                    await asyncio.sleep(3)
                    await message_link.delete()
                    await client.process_commands(message)
                    return

    await client.process_commands(message)

@client.command(aliases = ['pc'])
@commands.has_permissions(manage_messages = True)
async def pacman(ctx,amount=2):
    amount = amount+1
    await ctx.channel.purge(limit=amount)
    message = await ctx.send(f"{ctx.author.mention}, a gobé le tchat. *Miam Miam*")
    await asyncio.sleep(2)
    await message.delete()

######################## LIST STATUS MANAGEMENT #########################

#voir si on peut pas ajouter commandes pour p et m
@client.command(aliases = ['os'])
@commands.has_permissions(manage_messages = True)
async def opensales(ctx,people,time):
    people = people.lower().strip('p')
    time = time.lower().strip('m')
    await ctx.message.delete()
    if len(client.list_enchere) != 0:
        message = await ctx.send("Merci de terminer la liste avant d'en ouvrir une autre.")
        await asyncio.sleep(4)
        await message.delete()
        return
    if client.list_status == True:
        message = await ctx.send("Tu ne peux pas ouvrir une liste déjà ouverte.")
        await asyncio.sleep(4)
        await message.delete()
        return
    client.list_status = True
    await ctx.send(f"La liste a été ouverte par {ctx.author.mention} au maximum de {people} personnes. Vous avez {time} minutes pour vous inscrire ...\n\
        Infos commandes: $add pour s'inscrire | $r pour se retirer.")
    time = int(time)*60
    timer = 0
    #timer qui check chaque seconde état de la liste et cloture si liste pleine ou fin timer
    while client.list_status == True:
        await asyncio.sleep(1)
        timer +=1
        if timer == int(time):
            await closesales(ctx)
            break
        if len(client.list_enchere) == int(people):
            await closesales(ctx)
            break

@client.command(aliases = ['op'])
@commands.has_permissions(manage_messages = True)
async def open_people(ctx,people):
    await ctx.message.delete()
    people = people.lower().strip('p')
    if len(client.list_enchere) != 0:
        message = await ctx.send("Merci de terminer la liste avant d'en ouvrir une autre.")
        await asyncio.sleep(4)
        await message.delete()
        return
    if client.list_status == True:
        message = await ctx.send("Tu ne peux pas ouvrir une liste déjà ouverte.")
        await asyncio.sleep(4)
        await message.delete()
        return
    client.list_status = True
    await ctx.send(f"La liste a été ouverte par {ctx.author.mention} au maximum de {people} personnes.\n\
        Infos commandes: $add pour s'inscrire | $r pour se retirer.")
    
    while client.list_status == True:
        await asyncio.sleep(1)
        if len(client.list_enchere) == int(people):
            await closesales(ctx)
            break


@client.command(aliases = ['ot'])
@commands.has_permissions(manage_messages = True)
async def open_time(ctx,time):
    await ctx.message.delete()
    time = time.lower().strip('m')

    if len(client.list_enchere) != 0:
        message = await ctx.send("Merci de terminer la liste avant d'en ouvrir une autre.")
        await asyncio.sleep(4)
        await message.delete()
        return
    if client.list_status == True:
        message = await ctx.send("Vous ne peux pas ouvrir une liste déjà ouverte.")
        await asyncio.sleep(4)
        await message.delete()
        return
    client.list_status = True
    await ctx.send(f"La liste a été ouverte par {ctx.author.mention}. Vous avez {time} minutes pour vous inscrire ...\n\
        Infos commandes: $add pour s'inscrire | $r pour se retirer.")

    time = int(time)*60
    timer = 0
    while client.list_status == True:
        await asyncio.sleep(1)
        timer +=1
        if timer == int(time):
            await closesales(ctx)
            break

@client.command(aliases = ['cs'])
@commands.has_permissions(manage_messages = True)
async def humanclosesales(ctx):
    await ctx.message.delete()
    if client.list_status == True:
        await closesales(ctx)
    else:
        message = await ctx.send("La liste est déjà fermée...")
        await asyncio.sleep(3)
        await message.delete()

async def closesales(ctx):
    client.list_status = False
    await ctx.send(f"La liste a été fermée. Veuillez attendre la prochaine ouverture pour vous inscrire.")
    
    await message_fixe(ctx)
    client.counter = 0

    await next(ctx)


###################### LIST MEMBER MANAGEMENT ADDIND-REMOVE ###################

@client.command()
async def add(ctx):
    await ctx.message.delete()
    if ctx.author in client.list_enchere and client.list_status:
        message = await ctx.send(f"Tu ne peux pas t'inscrires 2 fois dans la liste")
        await asyncio.sleep(3)
        await message.delete()

    elif ctx.author not in client.list_enchere and client.list_status:
        client.list_enchere.append(ctx.author)
        message = await ctx.send(f"{ctx.author.mention}, s'est inscrit(e) à la liste. Tu es en position n°" +\
         str(int(client.list_enchere.index(ctx.author)+1)))
        await asyncio.sleep(3)
        await message.delete()

    elif not client.list_status:
        message = await ctx.send(f"La liste n'est pas ouverte, tu ne peux pas t'inscrire.")
        await asyncio.sleep(3)
        await message.delete()

@client.command(aliases = ['r'])
async def remove(ctx):
    await ctx.message.delete()
    if ctx.author in client.list_enchere:
        client.list_enchere.remove(ctx.author)
        message = await ctx.send(f"{ctx.author.mention}, a été desinscrit(e) de la liste.")
        await asyncio.sleep(3)
        await message.delete()
    else:
        message = await ctx.send(f"A quoi bon se désinscrire si tu n'es pas dans la liste...")
        await asyncio.sleep(4)
        await message.delete()

@client.command(aliases = ['next','n'])
@commands.has_permissions(manage_messages = True)
async def unto_next(ctx):
    if client.vendeur_actuel != None:
        await ctx.message.delete()
        await ctx.send("Pas de réponse... On passe au suivant !")
        await next(ctx)

    elif client.list_enchere == []:
        await ctx.message.delete()
        await ctx.send("La liste est vide vous ne pouvez pas donner le tour au néant...")
        return
    else:
        await ctx.message.delete()
        await ctx.send("Pas de réponse... On passe au suivant !")
        await next(ctx)

async def next(ctx):
    if client.list_status == True:
        await ctx.send("Tu ne peux pas nexter si la liste est encore ouverte... Merci de la fermer au préalable.")
        await asyncio.sleep(4)
        await message.delete()
    if client.list_enchere == []:
        await ctx.send("La liste est vide !")
        client.vendeur_actuel = None
        return
    if len(client.list_enchere) != 1:
        client.vendeur_actuel = client.list_enchere.pop(0)
        await ctx.send(f"C'est au tour de : {client.vendeur_actuel.mention} \n"\
            + f"Prépare toi, {client.list_enchere[0].mention}. Tu es le prochain/la prochaine !")
        await ctx.send("--- Suivant.e.s : ---")
        await show_list(ctx)
    elif len(client.list_enchere) == 1:
        client.vendeur_actuel = client.list_enchere[0]
        client.list_enchere = []
        await ctx.send(f"C'est au tour de : {client.vendeur_actuel.mention} \n"\
            + "La liste se termine après ce vendeur/cette vendeuse.")

################### MANUALLY ADD PEOPLE COMMANDS ###################

@client.command(aliases = ['e'])
@commands.has_permissions(manage_messages = True)
async def end(ctx,member):
    await ctx.message.delete()
    if ctx.message.mentions[0] in client.list_enchere:
        message = await ctx.author.send(f"Tu ne peux pas inscrire une seconde fois {ctx.message.mentions[0].mention}.")
        await asyncio.sleep(3)
        await message.delete()
    else:
        client.list_enchere.append(ctx.message.mentions[0])
        await ctx.author.send(f"Tu viens d'ajouter en soumsoum {ctx.message.mentions[0].mention}.")
        await ctx.message.mentions[0].send(f"Vous avez été ajouté en fin de liste par {ctx.author.mention}.")


@client.command(aliases = ['prio'])
@commands.has_permissions(manage_messages = True)
async def priority(ctx,people):
    await ctx.message.delete()
    if len(client.list_enchere) != 0:
        temp_member = client.list_enchere[0]
        if ctx.message.mentions[0] in client.list_enchere:
            client.list_enchere.remove(ctx.message.mentions[0])
            client.list_enchere.insert(0, ctx.message.mentions[0])
            await ctx.send(f"{ctx.message.mentions[0].mention}, passera en priorité après cette vente. Merci de votre compréhension.\n"\
                f"{temp_member.mention}. Promis tu passes après :).")
        else:
            client.list_enchere.insert(0, ctx.message.mentions[0])
            await ctx.send(f"{ctx.message.mentions[0].mention}, passera en priorité après cette vente. Merci de votre compréhension.\n"\
                f"{temp_member.mention}. Promis tu passes après :).")
    else:
        message_prio = await ctx.send(f"Si la liste est vide $e + tag fera l'affaire !")
        await asyncio.sleep(5)
        await message_prio.delete()

@client.command(aliases = ['nr'])
@commands.has_permissions(manage_messages = True)
async def next_report(ctx):
    await ctx.message.delete()
    if len(client.list_enchere) == 0:
        message_nr = await ctx.send("Tu ne peux pas next et mettre à la fin si cette personne est toute seule.")
        await asyncio.sleep(4)
        await message_nr.delete()

    await ctx.send(f"{client.vendeur_actuel.mention}, direction fin de liste ... A tout à l'heure !")
    client.list_enchere.append(client.vendeur_actuel)
    await next(ctx)


############### APPROVE SELL COMMANDS ######################

@client.command(aliases = ['adjc'])
@commands.has_permissions(manage_messages = True)
async def adjuger_clochettes(ctx,buyer,price):
    await ctx.message.delete()
    sale_number = await id_generator()
    await ctx.send(f"Adjugé à {ctx.message.mentions[0].mention} pour la somme de **{price}** clochettes au lot de {client.vendeur_actuel.mention} \n"+\
        f"*Numéro de référence: {sale_number}*")
    await dm_sales(ctx.message.mentions[0],client.vendeur_actuel,sale_number,0,price)
    
    client.counter +=1
    await message_spam(ctx)

    await next(ctx)
    if client.list_enchere == []:
        vendeur_actuel = None


@client.command(aliases = ['adjt'])
@commands.has_permissions(manage_messages = True)
async def adjuger_tickets(ctx,buyer,price):
    await ctx.message.delete()
    sale_number = await id_generator()
    await ctx.send(f"Adjugé à {ctx.message.mentions[0].mention} pour **{price}** ticket(s) NookMiles au lot de {client.vendeur_actuel.mention} \n"+\
        f"*Numéro de référence: {sale_number}*")
    await dm_sales(ctx.message.mentions[0],client.vendeur_actuel,sale_number,1,price)
    
    client.counter +=1
    await message_spam(ctx)
    
    await next(ctx)
    if client.list_enchere == []:
        vendeur_actuel = None


################# NON COMMANDS FUNCTION - LIST ################

# @client.command(aliases = ['sl'])
async def show_list(ctx):
    all_members = ""
    if len(client.list_enchere) != 1:
        for item in client.list_enchere[1:]:
            all_members += str(item)
            if client.list_enchere[-1] == item:
                all_members += "."
            else:
                all_members += ", "
        await ctx.send(f"{all_members}")
    elif len(client.list_enchere) == 1:
        await ctx.send("Il n'y a plus personne après.")

async def log_send(buyer,seller,sale_number,ToC,price):
    # #canal log discord ACNH
    channel = client.get_channel()
    if ToC == 0:
        await channel.send(f"Enchère n° {sale_number} au prix de {price} clochettes.\n"+\
        f"Vendeur : {seller.mention} \t Acheteur : {buyer.mention}")

    if ToC ==1:
        await channel.send(f"Enchère n° {sale_number} au prix de {price} ticket(s) NookMiles.\n"+\
        f"Vendeur : {seller.mention} \t Acheteur : {buyer.mention}")


async def dm_sales(buyer,seller,sale_number,ToC,price):
    buyer = client.get_user(buyer.id)
    seller = client.get_user(seller.id)

    if ToC == 0:
        await log_send(buyer,seller,sale_number,ToC,price)
        await buyer.send(f"Tu as une enchère pour un montant de {price} clochettes à payer auprès de {seller.name}.\n"+\
            f"*Voici ton numéro de référence: {sale_number}*")
        await seller.send(f"Tu as un lot à fournir à {buyer.name} pour un montant de {price} clochettes.\n"+\
            f"*Voici ton numéro de référence: {sale_number}*")

    if ToC == 1:
        await log_send(buyer,seller,sale_number,ToC,price)
        await buyer.send(f"Tu as une enchère pour un montant de {price} ticket(s) NookMiles à payer auprès de {seller.name}.\n"+\
            f"*Voici ton numéro de référence: {sale_number}*")
        await seller.send(f"Tu as un lot à fournir à {buyer.name} pour un montant de {price} ticket(s) NookMiles.\n"+\
            f"*Voici ton numéro de référence: {sale_number}*")


################### CHANNEL PROPERTIES ##################

@client.command()
@commands.has_permissions(manage_messages = True)
async def close(ctx):
    await ctx.message.delete()
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False
    overwrite.read_messages = True
    overwrite.attach_files = False
    overwrite.read_message_history = True
    overwrite.external_emojis = True
    member_role = discord.utils.get(ctx.guild.roles, name="Enchérisseurs")
    await ctx.channel.set_permissions(member_role, overwrite=overwrite)
    message = await ctx.send(f"Le salon à été fermé à l'écriture... Merci de votre compréhension.")

@client.command()
@commands.has_permissions(manage_messages = True)
async def open(ctx):
    await ctx.message.delete()
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = True
    overwrite.read_messages = True
    overwrite.attach_files = True
    overwrite.read_message_history = True
    overwrite.external_emojis = True
    members_role = discord.utils.get(ctx.guild.roles, name="Enchérisseurs")
    await ctx.channel.set_permissions(members_role, overwrite = overwrite)
    message = await ctx.send(f"Le salon vient d'être ouvert à l'écriture")

@client.command()
@commands.has_permissions(manage_messages = True)
async def pause(ctx):
    await close(ctx)
    await ctx.send("Enchères en pause, veuillez patienter le retour de votre Nook'priseur, merci.")

@client.command()
@commands.has_permissions(manage_messages = True)
async def resume(ctx):
    await open(ctx)
    await ctx.send("Nook'priseur de retour, on reprend !")
    await ctx.send(f"C'est au tour de {client.vendeur_actuel.mention}.\n")
    if client.list_enchere != []:
        await ctx.send(f"Prochain(e) : {client.list_enchere[0].mention}.")


async def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

############################ MESSAGES REMINDER ######################

@client.command(aliases = ["message","m"])
@commands.has_permissions(manage_messages = True)
async def message_spam_set(ctx,*,message):
    await ctx.message.delete()
    client.message_spam = str(message)
    message_prev = await ctx.send("Tu viens d'ajouter un message de prévention... Il s'affichera à interval régulier.\nPour le retirer utilise la commande $mr.")
    await asyncio.sleep(4)
    await message_prev.delete()

@client.command(aliases = ["mr"])
@commands.has_permissions(manage_messages = True)
async def message_spam_delete(ctx):
    await ctx.message.delete()
    client.message_spam = ""
    message = await ctx.send("Tu viens de retirer le message de prévention")
    await asyncio.sleep(4)
    await message.delete()

async def message_spam(ctx):
    if client.message_spam != "" and client.counter == 20:
        await message_nookP(ctx)
        await asyncio.sleep(5)
    elif client.counter == 20 or client.counter == 40:
        await message_fixe(ctx)
        await asyncio.sleep(15)
        if client.counter == 40:
            client.counter = 0

async def message_fixe(ctx):
    #channel ACNH
    channel = client.get_channel()
    members_role = discord.utils.get(ctx.guild.roles, name="Privé d'enchères")
    embed = discord.Embed(title="INFORMATIONS", color=0xff0000)
    embed.add_field(name= "---------------------------", value=f"Toute forme d'arnaque est passible de **Warn** et selon la gravité ou si récidive peut mener jusqu'à un **Ban**.\n\
    Il est aussi possible que vous obteniez le rôle {members_role.mention} qui vous interdira la participation aux enchères.\n\
    - Si vous êtes victime d'une **arnaque**, ou du non respect de votre transaction, merci de passer par {channel.mention}.\n\
    - Si vous pensez être arnaqué lors d'un échange en jeu (exemple ramasse l'argent mais ne vous donne pas votre du) , et avant la sauvegarde ne survienne mettez votre console en **veille** ou faites bouton maison de la manette > x > quitter le jeu !", inline=False)
    embed.add_field(name=":warning: ATTENTION :warning: ", value="Il est **STRICTEMENT INTERDIT** de proposer à la vente des Objets de type **HACK** ! Si tel était le cas, vous seriez directement **BAN** sans aucune forme de jugement.\n\
    Vous êtes toutes et tous priés de faire usage de __FAIRPLAY__ !\n\
    Nous savons que beaucoup d'entre vous ont des DAC plus que remplis, et savons aussi combien la communauté peut mal réagir face à une sorte de 'Concurrence déloyale' . Il est donc préférable d'agir avec retenue en ce qui concerne les achats en enchères, d'autant que vous n'êtes humainement pas capable d'honorer des dizaines de trades par jour.\n\
    Merci de votre compréhension.", inline=False)
    await ctx.send(embed=embed)
    await asyncio.sleep(15)

async def message_nookP(ctx):
    val_colour = random.randint(0, 0xFFFFFF)
    embed2 = discord.Embed(title="VOTRE NOOK'PRISEUR VOUS INFORME", color = val_colour)
    embed2.add_field(name = "------------------------", value =f"{client.message_spam}")
    await ctx.send(embed = embed2)



############################## ERROR HANDLES ###########################

@adjuger_tickets.error
async def adjuger_tickets_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send("Il manque soit le tag de l'acheteur soit le nombre de tickets.")
        await asyncio.sleep(3)
        await message.delete()


@adjuger_clochettes.error
async def adjuger_clochettes_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send("Il manque soit le tag de l'acheteur soit le nombre de clochettes")
        await asyncio.sleep(3)
        await message.delete()

@end.error
async def end_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send("Il manque le tag de la personne à ajouter !")
        await asyncio.sleep(3)
        await message.delete()

@opensales.error
async def end_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send("Il manque soit le nombre de personnes (1) soit le temps (2)!")
        await asyncio.sleep(5)
        await message.delete()

@open_time.error
async def time_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send("Il manque soit le temps en minutes !")
        await asyncio.sleep(5)
        await message.delete()

@open_people.error
async def people_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send("Il manque soit le nombre de personnes !")
        await asyncio.sleep(5)
        await message.delete()

@priority.error
async def priority_error(ctx,error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = await ctx.send("Il manque soit le tag de la personne à priotariser !")
        await asyncio.sleep(5)
        await message.delete()

client.run(TOKEN)