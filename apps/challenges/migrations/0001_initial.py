# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Challenge'
        db.create_table(u'challenges_challenge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 14, 0, 0), auto_now_add=True, blank=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(default='level 1', max_length=255, null=True, blank=True)),
            ('challenge_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('media_data', self.gf('django.db.models.fields.BinaryField')()),
            ('media_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('challenge_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('hint', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'challenges', ['Challenge'])

        # Adding model 'ChallengeResults'
        db.create_table(u'challenges_challengeresults', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 14, 0, 0), auto_now_add=True, blank=True)),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['challenges.Challenge'])),
            ('player', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('success', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'challenges', ['ChallengeResults'])

        # Adding model 'ChallengeSend'
        db.create_table(u'challenges_challengesend', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 1, 14, 0, 0), auto_now_add=True, blank=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_from', to=orm['auth.User'])),
            ('challenge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['challenges.Challenge'])),
            ('retry', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'challenges', ['ChallengeSend'])

        # Adding M2M table for field recipients on 'ChallengeSend'
        m2m_table_name = db.shorten_name(u'challenges_challengesend_recipients')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('challengesend', models.ForeignKey(orm[u'challenges.challengesend'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['challengesend_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'Challenge'
        db.delete_table(u'challenges_challenge')

        # Deleting model 'ChallengeResults'
        db.delete_table(u'challenges_challengeresults')

        # Deleting model 'ChallengeSend'
        db.delete_table(u'challenges_challengesend')

        # Removing M2M table for field recipients on 'ChallengeSend'
        db.delete_table(db.shorten_name(u'challenges_challengesend_recipients'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'challenges.challenge': {
            'Meta': {'object_name': 'Challenge'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'challenge_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'challenge_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'hint': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_data': ('django.db.models.fields.BinaryField', [], {}),
            'media_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'level 1'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'challenges.challengeresults': {
            'Meta': {'object_name': 'ChallengeResults'},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': u"orm['challenges.Challenge']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'player': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'success': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'challenges.challengesend': {
            'Meta': {'object_name': 'ChallengeSend'},
            'challenge': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['challenges.Challenge']"}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'}),
            'retry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_from'", 'to': u"orm['auth.User']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['challenges']