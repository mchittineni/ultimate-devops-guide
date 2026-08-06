---
title: "What is Chef?"
id: 53
category: "Configuration Management"
difficulty: "Intermediate"
tags:
  - devops
  - configuration-management
  - interview-questions
---

# What is Chef?

**Short answer:** Chef is a configuration management tool that describes desired state in Ruby-based "recipes" grouped into "cookbooks", applied by a `chef-client` agent that converges the node towards the state defined on the Chef Infra Server.

## Detail

**Terminology** (Chef leans hard on the cooking metaphor):

- **Resource** — a unit of configuration (`package`, `template`, `service`).
- **Recipe** — an ordered list of resources, written in a Ruby DSL.
- **Cookbook** — a package of recipes, templates, files, attributes, and tests.
- **Run list** — the ordered set of recipes and roles applied to a node.
- **Attributes** — configuration data with a precedence hierarchy (defaults, node, role, environment, override).
- **Data bags** — shared data, optionally encrypted for secrets.
- **Chef Infra Server** — stores cookbooks and node data; **Chef Workstation** is where you author and test.

**Two-phase execution** is Chef's distinctive behaviour: the compile phase evaluates the Ruby and builds a resource collection, then the converge phase executes those resources in order. Ruby code outside a resource block runs at compile time, which surprises newcomers.

Because recipes are Ruby, Chef offers more programmatic power than a pure DSL — and more rope. Its testing story is strong: **Test Kitchen** spins up real instances, **ChefSpec** unit-tests the resource collection, and **InSpec** verifies the converged system (and doubles as a standalone compliance tool).

## Example

```ruby
package 'nginx' do
  action :install
end

template '/etc/nginx/nginx.conf' do
  source 'nginx.conf.erb'
  owner  'root'
  mode   '0644'
  variables(workers: node['nginx']['workers'])
  notifies :reload, 'service[nginx]', :delayed
end

service 'nginx' do
  supports status: true, reload: true
  action [:enable, :start]
end
```

## Interview tips

- Compile versus converge phase is the classic Chef gotcha worth naming.
- InSpec is worth highlighting — it outlives Chef itself as a compliance-as-code tool.
- Position it against Puppet (Ruby DSL and imperative-friendly vs declarative) and Ansible (agent vs agentless).

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
