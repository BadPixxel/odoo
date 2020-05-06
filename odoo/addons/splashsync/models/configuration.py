# -*- coding: utf-8 -*-
#
#  This file is part of SplashSync Project.
#
#  Copyright (C) 2015-2020 Splash Sync  <www.splashsync.com>
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  For the full copyright and license information, please view the LICENSE
#  file that was distributed with this source code.
#

from odoo import api, models, fields, http


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _check_company_auto = True

    splash_ws_id = fields.Char(
        required=True,
        company_dependent=True,
        string="Server Identifier",
        default="ThisIsSplashWsId",
        help="Your Odoo Server Identifier, generated on your account."
    )
    splash_ws_key = fields.Char(
        required=True,
        company_dependent=True,
        string="Encryption Key",
        default="ThisIsYourEncryptionKeyForSplash"
    )
    splash_ws_expert = fields.Boolean(
        company_dependent=True,
        string="Advanced Mode",
        help="Check this to Enable Advanced Configuration"
    )
    splash_ws_host = fields.Char(
        company_dependent=True,
        string="Splash Server",
        default="https://www.splashsync.com/ws/soap",
        help="Url of your Splash Server (default: www.splashsync.com/ws/soap"
    )
    splash_ws_user = fields.Many2one(
        company_dependent=True,
        string="Webservice User",
        comodel_name="res.users",
        default="2",
        help="ID of Local User used by Splash"
    )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # Load Current Company Configuration
        config = self.env['res.config.settings'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        # Fetch Company Values
        res.update(
            splash_ws_id=config.splash_ws_id,
            splash_ws_key=config.splash_ws_key,
            splash_ws_expert=bool(config.splash_ws_expert),
            splash_ws_host=config.splash_ws_host,
            splash_ws_user=config.splash_ws_user.id,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # Load Current Company Configuration
        config = self.env['res.config.settings'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        # Update Company Values
        config.write({
            'splash_ws_id': self.splash_ws_id,
            'splash_ws_key': self.splash_ws_key,
            'splash_ws_expert': self.splash_ws_expert,
            'splash_ws_host': self.splash_ws_host,
            'splash_ws_user': self.splash_ws_user,
        })

    @staticmethod
    def get_base_url():
        from odoo import http

        return http.request.env['ir.config_parameter'].sudo().get_param('web.base.url')
