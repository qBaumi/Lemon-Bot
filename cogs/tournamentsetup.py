import discord
from discord.ext import commands
from discord import app_commands
from config import guilds

TOURNAMENT_TEXT_CATEGORY = "Tournament"
TOURNAMENT_VC_CATEGORY = "Tournament VCs"
CAPTAINS_ROLE_NAME = "Captains"


class TournamentSetup(commands.Cog, name="Tournament Setup"):
    def __init__(self, client):
        self.client = client

    def _normalize_text_channel_name(self, team_name: str) -> str:
        return team_name.strip().lower().replace(" ", "-")

    async def _send(self, interaction: discord.Interaction, message: str):
        await interaction.followup.send(message)

    async def _check_permission(self, interaction: discord.Interaction) -> bool:
        #solip7, .naughty 
        allowed_users = {260438629623660544, 198218633955115008}
        if interaction.user.id in allowed_users:
            return True
        if any(role.name == "Admins" for role in interaction.user.roles):
            return True
        await interaction.response.send_message("You don't have permission to use this command.")
        return False

    # ------------------------------------------------------------------
    # Helper: resolve a Discord member from a plain username string
    # Checks exact username, global name, and display name (case-insensitive) in this order
    # Returns the Member object or None
    # ------------------------------------------------------------------
    async def _resolve_member(self, guild: discord.Guild, name: str) -> discord.Member | None:
        name_lower = name.lower()
        results = await guild.query_members(name, limit=10)
        for m in results:
            if m.name.lower() == name_lower:
                return m
            if m.global_name and m.global_name.lower() == name_lower:
                return m
            if m.display_name.lower() == name_lower:
                return m
        return None

    # ------------------------------------------------------------------
    # Helper: parse the raw roster string into a list of (team_name, [usernames])
    # Expected format, teams separated by '|':
    #   Team A: user1, user2, user3 | Team B: user4, user5
    # Returns (teams, errors) where errors is a list of problem line strings
    # ------------------------------------------------------------------
    def _parse_roster(self, raw: str) -> tuple[list[tuple[str, list[str]]], list[str]]:
        teams: list[tuple[str, list[str]]] = []
        errors: list[str] = []

        if "\n" in raw or "\r" in raw:
            errors.append(
                "⚠️ Invalid roster format: use `|` to separate teams, not new lines."
            )
            return teams, errors

        entries = [entry.strip() for entry in raw.strip().split("|")]

        for entry in entries:
            if not entry:
                errors.append("⚠️ Empty team segment found. Remove repeated separators like `||`.")
                continue

            parts = entry.split(":", 1)
            if len(parts) != 2:
                errors.append(f"⚠️ Could not parse team segment (missing ':'): `{entry}`")
                continue
            team_name = parts[0].strip()
            usernames_raw = parts[1].strip()
            if not team_name:
                errors.append(f"⚠️ Empty team name in segment: `{entry}`")
                continue
            usernames = [u.strip() for u in usernames_raw.split(",") if u.strip()]
            if not usernames:
                errors.append(f"⚠️ No players listed for team `{team_name}`")
                continue
            teams.append((team_name, usernames))

        return teams, errors

    def _get_required_categories(
        self, guild: discord.Guild
    ) -> tuple[discord.CategoryChannel | None, discord.CategoryChannel | None, list[str]]:
        text_category = discord.utils.get(guild.categories, name=TOURNAMENT_TEXT_CATEGORY)
        vc_category = discord.utils.get(guild.categories, name=TOURNAMENT_VC_CATEGORY)

        missing = []
        if text_category is None:
            missing.append(f"`{TOURNAMENT_TEXT_CATEGORY}`")
        if vc_category is None:
            missing.append(f"`{TOURNAMENT_VC_CATEGORY}`")

        return text_category, vc_category, missing

    def _validate_templates(
        self,
        guild: discord.Guild,
        text_category: discord.CategoryChannel,
        vc_category: discord.CategoryChannel,
        template_role: discord.Role,
        template_text: discord.TextChannel,
        template_voice: discord.VoiceChannel,
    ) -> list[str]:
        """ Validates that the template role and channels exist and are in the correct categories. """    
        
        errors: list[str] = []
        if template_role.guild.id != guild.id:
            errors.append("template role not found in this server")
        if template_text.guild.id != guild.id:
            errors.append("template text channel not found in this server")
        if template_voice.guild.id != guild.id:
            errors.append("template voice channel not found in this server")
        if template_text.category_id != text_category.id:
            errors.append(
                f"text template channel `{template_text.name}` is not in **{TOURNAMENT_TEXT_CATEGORY}**"
            )
        if template_voice.category_id != vc_category.id:
            errors.append(
                f"voice template channel `{template_voice.name}` is not in **{TOURNAMENT_VC_CATEGORY}**"
            )

        return errors

    def _validate_role_hierarchy(
        self,
        guild: discord.Guild,
        template_role: discord.Role,
        captains_role: discord.Role,
    ) -> list[str]:
        """ Validates that the bot's top role is higher than the template role and that it has the required permissions. """
        
        errors: list[str] = []
        me = guild.me
        if me is None:
            errors.append("lemonbot member could not be resolved in this server")
            return errors

        if me.top_role <= template_role:
            errors.append(
                (
                    f"lemonbot top role `{me.top_role.name}` must be higher than template role "
                    f"`{template_role.name}` to create/move team roles"
                )
            )

        if me.top_role <= captains_role:
            errors.append(
                (
                    f"lemonbot top role `{me.top_role.name}` must be higher than captains role "
                    f"`{captains_role.name}` to assign captains"
                )
            )

        if not guild.me.guild_permissions.manage_roles:
            errors.append("lemonbot is missing Manage Roles permission")

        if not guild.me.guild_permissions.manage_channels:
            errors.append("lemonbot is missing Manage Channels permission")

        return errors

    def _build_overwrites_from_template(
        self,
        template_channel: discord.abc.GuildChannel,
        template_role: discord.Role,
        team_role: discord.Role,
    ) -> tuple[dict[discord.Role | discord.Member, discord.PermissionOverwrite], bool]:
        """ Takes the permission overwrites from the template channel and template role and builds new overwrites for the team role."""
        
        overwrites: dict[discord.Role | discord.Member, discord.PermissionOverwrite] = {}
        found_template_role = False
        for target, overwrite in template_channel.overwrites.items():
            if isinstance(target, discord.Role) and target.id == template_role.id:
                overwrites[team_role] = overwrite
                found_template_role = True
            else:
                overwrites[target] = overwrite
        return overwrites, found_template_role

    def _get_team_collisions(
        self,
        guild: discord.Guild,
        text_category: discord.CategoryChannel,
        vc_category: discord.CategoryChannel,
        team_name: str,
    ) -> list[str]:
        """ Checks if a role or channels with the given team name already exist. """

        existing_role = discord.utils.get(guild.roles, name=team_name)
        text_channel_name = self._normalize_text_channel_name(team_name)
        existing_text = discord.utils.get(text_category.channels, name=text_channel_name)
        existing_vc = discord.utils.get(vc_category.channels, name=team_name)

        collisions = []
        if existing_role:
            collisions.append(f"role `{team_name}`")
        if existing_text:
            collisions.append(
                f"text channel `{text_channel_name}` in **{TOURNAMENT_TEXT_CATEGORY}**"
            )
        if existing_vc:
            collisions.append(
                f"voice channel `{team_name}` in **{TOURNAMENT_VC_CATEGORY}**"
            )
        return collisions

    async def _create_team_role(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        team_name: str,
        template_role: discord.Role,
    ) -> discord.Role | None:
        try:
            team_role = await guild.create_role(
                name=team_name,
                permissions=template_role.permissions,
                colour=template_role.colour,
                hoist=template_role.hoist,
                mentionable=template_role.mentionable,
                reason=f"Tournament setup: role for team {team_name}",
            )
            target_position = max(1, template_role.position - 1)
            await team_role.edit(
                position=target_position,
                reason=f"Tournament setup: move role {team_name} under template role",
            )
            await self._send(interaction, f"✅ Created role **{team_name}**")
            return team_role
        except discord.Forbidden:
            await self._send(
                interaction,
                f"❌ Failed to create role `{team_name}`. Skipping team.",
            )
            return None
        except discord.HTTPException as exc:
            await self._send(
                interaction,
                f"❌ Failed to create role `{team_name}` due to API error: `{exc}`. Skipping team.",
            )
            return None

    async def _assign_team_role(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        usernames: list[str],
        team_role: discord.Role,
        team_name: str,
    ) -> tuple[int, int]:
        assigned_count = 0
        not_found_count = 0
        role_assignment_blocked = False
        for username in usernames:
            if role_assignment_blocked:
                break

            member = await self._resolve_member(guild, username)
            if member is None:
                await self._send(interaction, f"⚠️ User not found: `{username}` — skipping.")
                not_found_count += 1
                continue

            try:
                await member.add_roles(
                    team_role,
                    reason=f"Tournament setup: assigned to team {team_name}",
                )
                await self._send(
                    interaction,
                    f"✅ Assigned role **{team_name}** to {member.mention}",
                )
                assigned_count += 1
            except discord.Forbidden:
                await self._send(
                    interaction,
                    (
                        f"❌ Role assignment for team **{team_name}** was blocked unexpectedly. "
                        "Skipping remaining role assignments for this team; check member-level restrictions or server role configuration."
                    ),
                )
                role_assignment_blocked = True
            except discord.HTTPException as exc:
                await self._send(
                    interaction,
                    f"❌ Failed to assign role to {member.mention}: `{exc}`.",
                )
        return assigned_count, not_found_count

    async def _assign_captain_role(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        team_name: str,
        usernames: list[str],
        captains_role: discord.Role,
    ) -> int:
        if not usernames:
            return 0

        captain_username = usernames[0]
        captain_member = await self._resolve_member(guild, captain_username)
        if captain_member is None:
            await self._send(
                interaction,
                f"⚠️ Captain user not found for team `{team_name}`: `{captain_username}`.",
            )
            return 0

        if captains_role in captain_member.roles:
            await self._send(
                interaction,
                f"ℹ️ {captain_member.mention} already has **{captains_role.name}**.",
            )
            return 0

        try:
            await captain_member.add_roles(
                captains_role,
                reason=f"Tournament setup: first listed player is captain for {team_name}",
            )
            await self._send(
                interaction,
                f"✅ Assigned **{captains_role.name}** to {captain_member.mention} (first listed player).",
            )
            return 1
        except discord.Forbidden:
            await self._send(
                interaction,
                (
                    f"❌ Could not assign **{captains_role.name}** to {captain_member.mention}. "
                    "Check role hierarchy and permissions."
                ),
            )
            return 0
        except discord.HTTPException as exc:
            await self._send(
                interaction,
                f"❌ Failed to assign **{captains_role.name}** to {captain_member.mention}: `{exc}`.",
            )
            return 0

    async def _create_team_text_channel(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        text_category: discord.CategoryChannel,
        team_name: str,
        team_role: discord.Role,
        template_text_channel: discord.TextChannel,
        template_role: discord.Role,
    ) -> bool:
        text_overwrites, found_template_role = self._build_overwrites_from_template(
            template_text_channel,
            template_role,
            team_role,
        )
        if not found_template_role:
            await self._send(
                interaction,
                (
                    f"❌ Template text channel `{template_text_channel.name}` does not include "
                    f"an overwrite for role `{template_role.name}`. Skipping text channel for `{team_name}`."
                ),
            )
            return False
        text_channel_name = self._normalize_text_channel_name(team_name)
        try:
            text_ch = await guild.create_text_channel(
                name=text_channel_name,
                category=text_category,
                overwrites=text_overwrites,
                reason=f"Tournament setup: text channel for team {team_name}",
            )
            await self._send(
                interaction,
                f"✅ Created text channel {text_ch.mention} in **{TOURNAMENT_TEXT_CATEGORY}**",
            )
            return True
        except discord.Forbidden:
            await self._send(
                interaction,
                f"❌ Failed to create text channel for team `{team_name}`.",
            )
            return False
        except discord.HTTPException as exc:
            await self._send(
                interaction,
                f"❌ Failed to create text channel for `{team_name}`: `{exc}`.",
            )
            return False

    async def _create_team_voice_channel(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        vc_category: discord.CategoryChannel,
        team_name: str,
        team_role: discord.Role,
        template_voice_channel: discord.VoiceChannel,
        template_role: discord.Role,
    ) -> bool:
        vc_overwrites, found_template_role = self._build_overwrites_from_template(
            template_voice_channel,
            template_role,
            team_role,
        )
        if not found_template_role:
            await self._send(
                interaction,
                (
                    f"❌ Template voice channel `{template_voice_channel.name}` does not include "
                    f"an overwrite for role `{template_role.name}`. Skipping voice channel for `{team_name}`."
                ),
            )
            return False
        try:
            vc_ch = await guild.create_voice_channel(
                name=team_name,
                category=vc_category,
                overwrites=vc_overwrites,
                reason=f"Tournament setup: voice channel for team {team_name}",
            )
            await self._send(
                interaction,
                f"✅ Created voice channel **{vc_ch.name}** in **{TOURNAMENT_VC_CATEGORY}**",
            )
            return True
        except discord.Forbidden as exc:
            await self._send(
                interaction,
                (
                    f"❌ Failed to create voice channel for `{team_name}`.\n"
                    f"Status: `{getattr(exc, 'status', 'unknown')}`\n"
                    f"Code: `{getattr(exc, 'code', 'unknown')}`\n"
                    f"Details: `{getattr(exc, 'text', 'no error text returned')}`"
                ),
            )
            return False
        except discord.HTTPException as exc:
            await self._send(
                interaction,
                f"❌ Failed to create voice channel for `{team_name}`: `{exc}`.",
            )
            return False

    async def _process_team(
        self,
        interaction: discord.Interaction,
        guild: discord.Guild,
        text_category: discord.CategoryChannel,
        vc_category: discord.CategoryChannel,
        template_role: discord.Role,
        template_text_channel: discord.TextChannel,
        template_voice_channel: discord.VoiceChannel,
        captains_role: discord.Role,
        team_name: str,
        usernames: list[str],
    ) -> dict[str, int]:
        stats = {
            "teams_skipped": 0,
            "roles_created": 0,
            "text_channels_created": 0,
            "voice_channels_created": 0,
            "users_assigned": 0,
            "users_not_found": 0,
            "captains_assigned": 0,
        }
        await self._send(interaction, f"─────────────\n**Team: {team_name}**")

        collisions = self._get_team_collisions(
            guild, text_category, vc_category, team_name
        )
        if collisions:
            await self._send(
                interaction,
                f"⏭️ Skipping **{team_name}** — the following already exist: "
                + ", ".join(collisions),
            )
            stats["teams_skipped"] += 1
            return stats

        team_role = await self._create_team_role(
            interaction,
            guild,
            team_name,
            template_role,
        )
        if team_role is None:
            stats["teams_skipped"] += 1
            return stats
        stats["roles_created"] += 1

        assigned_count, not_found_count = await self._assign_team_role(
            interaction, guild, usernames, team_role, team_name
        )
        stats["users_assigned"] += assigned_count
        stats["users_not_found"] += not_found_count
        stats["captains_assigned"] += await self._assign_captain_role(
            interaction,
            guild,
            team_name,
            usernames,
            captains_role,
        )

        text_created = await self._create_team_text_channel(
            interaction,
            guild,
            text_category,
            team_name,
            team_role,
            template_text_channel,
            template_role,
        )
        if text_created:
            stats["text_channels_created"] += 1

        voice_created = await self._create_team_voice_channel(
            interaction,
            guild,
            vc_category,
            team_name,
            team_role,
            template_voice_channel,
            template_role,
        )
        if voice_created:
            stats["voice_channels_created"] += 1

        return stats

    # ------------------------------------------------------------------
    # /tournamentsetup command
    # ------------------------------------------------------------------
    @app_commands.command(
        name="tournamentsetup",
        description="Set up tournament team roles and channels from template role/channels.",
    )
    @app_commands.describe(
        template_role="Role template to copy role settings from",
        template_text_channel=(
            "Text channel template whose overwrites are copied (must be in Tournament category)"
        ),
        template_voice_channel=(
            "Voice channel template whose overwrites are copied (must be in Tournament VCs category)"
        ),
        roster=(
            "Pipe-separated team roster. "
            "Format: Team A: user1, user2 | Team B: user3, user4"
        ),
    )
    async def tournament_setup(
        self,
        interaction: discord.Interaction,
        template_role: discord.Role,
        template_text_channel: discord.TextChannel,
        template_voice_channel: discord.VoiceChannel,
        roster: str,
    ):
        if not await self._check_permission(interaction):
            return

        await interaction.response.defer(thinking=True)

        guild = interaction.guild

        if guild is None:
            await self._send(
                interaction,
                "❌ This command can only be used inside a server.",
            )
            return

        # ── Step 1: verify both categories exist ────────────────────────
        text_category, vc_category, missing = self._get_required_categories(guild)

        if missing:
            await self._send(
                interaction,
                f"❌ Cannot proceed — the following category/categories were not found on this server: "
                f"{', '.join(missing)}\n"
                "Please create them manually and re-run the command."
            )
            return

        await self._send(
            interaction,
            f"✅ Found categories **{TOURNAMENT_TEXT_CATEGORY}** and **{TOURNAMENT_VC_CATEGORY}**. Starting setup…"
        )

        # ── Step 1b: validate provided template objects ───────────────
        template_errors = self._validate_templates(
            guild,
            text_category,
            vc_category,
            template_role,
            template_text_channel,
            template_voice_channel,
        )
        if template_errors:
            await self._send(
                interaction,
                (
                    "❌ Cannot proceed — template validation failed: "
                    f"{'; '.join(template_errors)}"
                ),
            )
            return

        captains_role = discord.utils.get(guild.roles, name=CAPTAINS_ROLE_NAME)
        if captains_role is None:
            await self._send(
                interaction,
                f"❌ Cannot proceed — role `{CAPTAINS_ROLE_NAME}` was not found.",
            )
            return

        hierarchy_errors = self._validate_role_hierarchy(guild, template_role, captains_role)
        if hierarchy_errors:
            await self._send(
                interaction,
                (
                    "❌ Cannot proceed — role hierarchy/permission check failed: "
                    f"{'; '.join(hierarchy_errors)}"
                ),
            )
            return

        await self._send(
            interaction,
            (
                "✅ Found template role/channel objects. "
                "Team roles/channels will be created from template settings."
            ),
        )

        # ── Step 2: parse the roster ────────────────────────────────────
        teams, parse_errors = self._parse_roster(roster)

        if parse_errors:
            await self._send(
                interaction,
                "⚠️ **Roster parse warnings:**\n" + "\n".join(parse_errors)
            )

        if not teams:
            await self._send(interaction, "❌ No valid teams found in the roster. Aborting.")
            return

        summary = {
            "teams_total": len(teams),
            "teams_skipped": 0,
            "roles_created": 0,
            "text_channels_created": 0,
            "voice_channels_created": 0,
            "users_assigned": 0,
            "users_not_found": 0,
            "captains_assigned": 0,
        }

        # ── Step 3: process each team ───────────────────────────────────
        for team_name, usernames in teams:
            team_stats = await self._process_team(
                interaction,
                guild,
                text_category,
                vc_category,
                template_role,
                template_text_channel,
                template_voice_channel,
                captains_role,
                team_name,
                usernames,
            )
            for key in (
                "teams_skipped",
                "roles_created",
                "text_channels_created",
                "voice_channels_created",
                "users_assigned",
                "users_not_found",
                "captains_assigned",
            ):
                summary[key] += team_stats[key]

        await self._send(interaction, "─────────────\n✅ Tournament setup complete.")
        await self._send(
            interaction,
            (
                "📊 **Summary**\n"
                f"Teams parsed: **{summary['teams_total']}**\n"
                f"Teams skipped: **{summary['teams_skipped']}**\n"
                f"Roles created: **{summary['roles_created']}**\n"
                f"Text channels created: **{summary['text_channels_created']}**\n"
                f"Voice channels created: **{summary['voice_channels_created']}**\n"
                f"Users assigned: **{summary['users_assigned']}**\n"
                f"Users not found: **{summary['users_not_found']}**\n"
                f"Captains assigned: **{summary['captains_assigned']}**"
            ),
        )


async def setup(client):
    await client.add_cog(TournamentSetup(client), guilds=guilds)
