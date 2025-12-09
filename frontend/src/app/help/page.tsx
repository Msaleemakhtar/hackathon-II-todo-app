"use client";

import withAuth from '@/components/withAuth';
import { HelpCircle, Mail, Phone, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';

function HelpPage() {
  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <HelpCircle className="h-6 w-6 text-coral" />
          <h1 className="text-2xl font-bold text-gray-900">Help & Support</h1>
        </div>
        <p className="text-gray-600">Get help with using the Task Management Dashboard</p>
      </div>

      {/* Help Sections */}
      <div className="space-y-6">
        {/* FAQ Section */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">Frequently Asked Questions</h2>
          <div className="space-y-4">
            <div>
              <h3 className="font-medium text-gray-900 mb-2">How do I create a new task?</h3>
              <p className="text-sm text-gray-600">
                Click the "Add Task" button on the Dashboard, My Tasks, or Vital Tasks page. Fill in the task details and click "Create Task".
              </p>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">How do I mark a task as complete?</h3>
              <p className="text-sm text-gray-600">
                Click on a task to open the details modal, then click "Mark as Complete" button.
              </p>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">What are Vital Tasks?</h3>
              <p className="text-sm text-gray-600">
                Vital Tasks are tasks marked with high priority. They appear on the Vital Tasks page for quick access to your most important items.
              </p>
            </div>

            <div>
              <h3 className="font-medium text-gray-900 mb-2">How do I change my password?</h3>
              <p className="text-sm text-gray-600">
                Go to Settings from the sidebar, then switch to the "Change Password" tab. Enter your current password and new password to update.
              </p>
            </div>
          </div>
        </div>

        {/* Contact Support */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">Contact Support</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-auto flex-col gap-2 py-4">
              <Mail className="h-6 w-6 text-coral" />
              <span className="font-medium">Email Support</span>
              <span className="text-xs text-gray-500">support@taskdashboard.com</span>
            </Button>

            <Button variant="outline" className="h-auto flex-col gap-2 py-4">
              <Phone className="h-6 w-6 text-coral" />
              <span className="font-medium">Phone Support</span>
              <span className="text-xs text-gray-500">+1 (555) 123-4567</span>
            </Button>

            <Button variant="outline" className="h-auto flex-col gap-2 py-4">
              <MessageSquare className="h-6 w-6 text-coral" />
              <span className="font-medium">Live Chat</span>
              <span className="text-xs text-gray-500">Available 24/7</span>
            </Button>
          </div>
        </div>

        {/* Quick Links */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-900">Quick Links</h2>
          <div className="space-y-2">
            <a href="#" className="block text-coral hover:text-coral-600 text-sm">
              → Getting Started Guide
            </a>
            <a href="#" className="block text-coral hover:text-coral-600 text-sm">
              → Video Tutorials
            </a>
            <a href="#" className="block text-coral hover:text-coral-600 text-sm">
              → API Documentation
            </a>
            <a href="#" className="block text-coral hover:text-coral-600 text-sm">
              → Privacy Policy
            </a>
            <a href="#" className="block text-coral hover:text-coral-600 text-sm">
              → Terms of Service
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default withAuth(HelpPage);
