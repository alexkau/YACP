# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'PlanCourse.course'
        db.delete_column(u'planner_plancourse', 'course_id')

        # Adding field 'PlanCourse.year'
        db.add_column(u'planner_plancourse', 'year',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'PlanCourse.course'
        db.add_column(u'planner_plancourse', 'course',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['courses.Course']),
                      keep_default=False)

        # Deleting field 'PlanCourse.year'
        db.delete_column(u'planner_plancourse', 'year')


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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'planner.plancourse': {
            'Meta': {'object_name': 'PlanCourse'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'semester': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'planner_courses'", 'to': u"orm['planner.PlanUser']"}),
            'year': ('django.db.models.fields.IntegerField', [], {})
        },
        u'planner.planuser': {
            'Meta': {'object_name': 'PlanUser'},
            'first_semester': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'first_year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selections': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['scheduler.SavedSelection']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'planuser'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'scheduler.savedselection': {
            'Meta': {'object_name': 'SavedSelection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internal_blocked_times': ('django.db.models.fields.TextField', [], {'db_index': 'True'}),
            'internal_section_ids': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '1024', 'db_index': 'True'})
        }
    }

    complete_apps = ['planner']