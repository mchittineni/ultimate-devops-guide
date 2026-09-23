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

- **Resource** - a unit of configuration (`package`, `template`, `service`).
- **Recipe** - an ordered list of resources, written in a Ruby DSL.
- **Cookbook** - a package of recipes, templates, files, attributes, and tests.
- **Run list** - the ordered set of recipes and roles applied to a node.
- **Attributes** - configuration data with a precedence hierarchy (defaults, node, role, environment, override).
- **Data bags** - shared data, optionally encrypted for secrets.
- **Chef Infra Server** - stores cookbooks and node data; **Chef Workstation** is where you author and test.

**Two-phase execution** is Chef's distinctive behaviour: the compile phase evaluates the Ruby and builds a resource collection, then the converge phase executes those resources in order. Ruby code outside a resource block runs at compile time, which surprises newcomers.

Because recipes are Ruby, Chef offers more programmatic power than a pure DSL - and more rope. Commercially, Chef is owned by Progress: the source code is Apache-2.0, but Progress's official binaries (Chef Infra Client, InSpec) require a commercial licence for production use, and **Cinc** is the community-built, freely redistributable distribution of the same code. That licensing, and a smaller community than Ansible's, is why Chef appears mostly in established estates rather than new projects. Its testing story is strong: **Test Kitchen** spins up real instances, **ChefSpec** unit-tests the resource collection, and **InSpec** verifies the converged system (and doubles as a standalone compliance tool).

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
- InSpec is worth highlighting - it is used on its own as a compliance-as-code tool (note that current InSpec releases also need a Progress licence; Cinc Auditor is the free build).
- Position it against Puppet (Ruby DSL and imperative-friendly vs declarative) and Ansible (agent vs agentless).

<!-- BEGIN GENERATED RELATED TOPICS -->

## Related Concepts

- [[How do you promote a release across dev, staging, and production?]] (`#399`): [How do you promote a release across dev, staging, and production?](../cicd/how-do-you-promote-a-release-across-dev-staging-and-production.md)
- [[Why does a build pass locally but fail in CI?]] (`#397`): [Why does a build pass locally but fail in CI?](../cicd/why-does-a-build-pass-locally-but-fail-in-ci.md)
- [[What is Continuous Integration?]] (`#3`): [What is Continuous Integration?](../core-devops-concepts/what-is-continuous-integration.md)

<!-- END GENERATED RELATED TOPICS -->

---

[⬅ Back to Configuration Management](./README.md) · [All topics](../README.md)
